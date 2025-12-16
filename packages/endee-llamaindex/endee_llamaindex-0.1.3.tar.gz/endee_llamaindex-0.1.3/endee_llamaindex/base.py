import logging
from collections import Counter
from functools import partial
import json
from typing import Any, Callable, Dict, List, Optional, cast

from llama_index.core.bridge.pydantic import PrivateAttr
from llama_index.core.schema import BaseNode, MetadataMode, TextNode
from llama_index.core.vector_stores.types import (
    BasePydanticVectorStore,
    MetadataFilters,
    VectorStoreQuery,
    VectorStoreQueryMode,
    VectorStoreQueryResult,
)
from llama_index.core.vector_stores.utils import (
    DEFAULT_TEXT_KEY,
    legacy_metadata_dict_to_node,
    metadata_dict_to_node,
    node_to_metadata_dict,
)

from datetime import datetime

def _import_endee() -> Any:
    """
    Try to import endee module. If it's not already installed, instruct user how to install.
    """
    try:
        import endee
        from endee.endee import Endee
    except ImportError as e:
        raise ImportError(
            "Could not import endee python package. "
            "Please install it with `pip install endee`."
        ) from e
    return endee

ID_KEY = "id"
VECTOR_KEY = "values"
SPARSE_VECTOR_KEY = "sparse_values"
METADATA_KEY = "metadata"

DEFAULT_BATCH_SIZE = 100

_logger = logging.getLogger(__name__)

from llama_index.core.vector_stores.types import MetadataFilter, FilterOperator

reverse_operator_map = {
    FilterOperator.EQ: "$eq",
    FilterOperator.NE: "$ne",
    FilterOperator.GT: "$gt",
    FilterOperator.GTE: "$gte",
    FilterOperator.LT: "$lt",
    FilterOperator.LTE: "$lte",
    FilterOperator.IN: "$in",
    FilterOperator.NIN: "$nin",
}



def build_dict(input_batch: List[List[int]]) -> List[Dict[str, Any]]:
    """
    Build a list of sparse dictionaries from a batch of input_ids.

    NOTE: taken from https://www.pinecone.io/learn/hybrid-search-intro/.

    """
    # store a batch of sparse embeddings
    sparse_emb = []
    # iterate through input batch
    for token_ids in input_batch:
        indices = []
        values = []
        # convert the input_ids list to a dictionary of key to frequency values
        d = dict(Counter(token_ids))
        for idx in d:
            indices.append(idx)
            values.append(float(d[idx]))
        sparse_emb.append({"indices": indices, "values": values})
    # return sparse_emb list
    return sparse_emb


def generate_sparse_vectors(
    context_batch: List[str], tokenizer: Callable
) -> List[Dict[str, Any]]:
    """
    Generate sparse vectors from a batch of contexts.

    NOTE: taken from https://www.pinecone.io/learn/hybrid-search-intro/.

    """
    # create batch of input_ids
    inputs = tokenizer(context_batch)["input_ids"]
    # create sparse dictionaries
    return build_dict(inputs)


# Supported sparse embedding models
SUPPORTED_SPARSE_MODELS = {
    "splade_pp": "prithivida/Splade_PP_en_v1",
    "splade_cocondenser": "naver/splade-cocondenser-ensembledistil",
    "bert_base": "bert-base-uncased",
    "distilbert": "distilbert-base-uncased",
    "minilm": "sentence-transformers/all-MiniLM-L6-v2",
    "mpnet": "sentence-transformers/all-mpnet-base-v2",
    "roberta": "roberta-base",
    "xlm_roberta": "xlm-roberta-base",
}


def _initialize_sparse_encoder_fastembed(
    model_name: str,
    batch_size: int = 256,
    cache_dir: Optional[str] = None,
    threads: Optional[int] = None,
) -> Callable:
    """
    Initialize a sparse encoder using FastEmbed (recommended for SPLADE models).
    
    Args:
        model_name: Model identifier or alias
        batch_size: Batch size for encoding
        cache_dir: Directory to cache model files
        threads: Number of threads to use
        
    Returns:
        Callable function that generates sparse vectors from text
    """
    try:
        from fastembed.sparse.sparse_text_embedding import SparseTextEmbedding
    except ImportError as e:
        raise ImportError(
            "Could not import FastEmbed. "
            "Please install it with `pip install fastembed` or "
            "`pip install fastembed-gpu` for GPU support."
        ) from e

    # Resolve model name from alias if needed
    resolved_model_name = SUPPORTED_SPARSE_MODELS.get(model_name, model_name)
    
    # Try GPU first, fallback to CPU
    try:
        model = SparseTextEmbedding(
            resolved_model_name,
            cache_dir=cache_dir,
            threads=threads,
            providers=["CUDAExecutionProvider"],
        )
        _logger.info(f"Initialized sparse encoder '{resolved_model_name}' on GPU")
    except Exception:
        model = SparseTextEmbedding(
            resolved_model_name, 
            cache_dir=cache_dir, 
            threads=threads
        )
        _logger.info(f"Initialized sparse encoder '{resolved_model_name}' on CPU")

    def compute_vectors(texts: List[str]) -> tuple:
        """Compute sparse vectors (indices, values) for a list of texts."""
        embeddings = model.embed(texts, batch_size=batch_size)
        indices = []
        values = []
        for embedding in embeddings:
            indices.append(embedding.indices.tolist())
            values.append(embedding.values.tolist())
        return indices, values

    return compute_vectors


def _initialize_sparse_encoder_transformers(
    model_name: str,
) -> Callable:
    """
    Initialize a sparse encoder using Transformers library.
    
    Args:
        model_name: Model identifier or alias
        
    Returns:
        Callable function that generates sparse vectors from text
    """
    try:
        import torch
        from transformers import AutoModelForMaskedLM, AutoTokenizer
    except ImportError as e:
        raise ImportError(
            "Could not import transformers library. "
            'Please install transformers with `pip install "transformers[torch]"`'
        ) from e

    # Resolve model name from alias if needed
    resolved_model_name = SUPPORTED_SPARSE_MODELS.get(model_name, model_name)
    
    tokenizer = AutoTokenizer.from_pretrained(resolved_model_name)
    model = AutoModelForMaskedLM.from_pretrained(resolved_model_name)
    
    if torch.cuda.is_available():
        model = model.to("cuda")
        _logger.info(f"Initialized sparse encoder '{resolved_model_name}' on GPU")
    else:
        _logger.info(f"Initialized sparse encoder '{resolved_model_name}' on CPU")

    def compute_vectors(texts: List[str]) -> tuple:
        """
        Compute sparse vectors from logits using ReLU, log, and max operations.
        """
        tokens = tokenizer(
            texts, 
            truncation=True, 
            padding=True, 
            max_length=512, 
            return_tensors="pt"
        )
        
        if torch.cuda.is_available():
            tokens = tokens.to("cuda")

        with torch.no_grad():
            output = model(**tokens)
            logits, attention_mask = output.logits, tokens.attention_mask
            relu_log = torch.log(1 + torch.relu(logits))
            weighted_log = relu_log * attention_mask.unsqueeze(-1)
            tvecs, _ = torch.max(weighted_log, dim=1)

        # Extract non-zero vectors and their indices
        indices = []
        values = []
        for batch in tvecs:
            nz_indices = batch.nonzero(as_tuple=True)[0].tolist()
            indices.append(nz_indices)
            values.append(batch[nz_indices].tolist())

        return indices, values

    return compute_vectors


def get_sparse_encoder(
    model_name: Optional[str] = None,
    use_fastembed: bool = True,
    batch_size: int = 256,
    cache_dir: Optional[str] = None,
    threads: Optional[int] = None,
) -> Optional[Callable]:
    """
    Get a sparse encoder function for the specified model.
    
    Args:
        model_name: Model name or alias (e.g., 'splade_pp', 'bert_base', or full model ID)
        use_fastembed: If True, use FastEmbed (recommended for SPLADE models), else use Transformers
        batch_size: Batch size for encoding
        cache_dir: Directory to cache model files
        threads: Number of threads to use
        
    Returns:
        Callable function that generates sparse vectors, or None if model_name is not provided
    """
    if model_name is None:
        return None
    
    if use_fastembed:
        return _initialize_sparse_encoder_fastembed(
            model_name=model_name,
            batch_size=batch_size,
            cache_dir=cache_dir,
            threads=threads,
        )
    else:
        return _initialize_sparse_encoder_transformers(model_name=model_name)


import_err_msg = (
    "`endee` package not found, please run `pip install endee` to install it.`"
)


class EndeeVectorStore(BasePydanticVectorStore):

    stores_text: bool = True
    flat_metadata: bool = False

    api_token: Optional[str]
    index_name: Optional[str]
    space_type: Optional[str]
    dimension: Optional[int]
    insert_kwargs: Optional[Dict]
    add_sparse_vector: bool
    text_key: str
    batch_size: int
    remove_text_from_metadata: bool
    hybrid: bool
    vocab_size: Optional[int]
    model_name: Optional[str]
    precision: Optional[str]
    key: Optional[str]

    _endee_index: Any = PrivateAttr()
    _sparse_encoder: Optional[Callable] = PrivateAttr(default=None)

    def __init__(
        self,
        endee_index: Optional[Any] = None,
        api_token: Optional[str] = None,
        index_name: Optional[str] = None,
        space_type: Optional[str] = "cosine",
        dimension: Optional[int] = None,
        insert_kwargs: Optional[Dict] = None,
        add_sparse_vector: bool = False,
        text_key: str = DEFAULT_TEXT_KEY,
        batch_size: int = DEFAULT_BATCH_SIZE,
        remove_text_from_metadata: bool = False,
        hybrid: bool = False,
        vocab_size: Optional[int] = None,
        model_name: Optional[str] = None,
        precision: Optional[str] = "medium",
        key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        insert_kwargs = insert_kwargs or {}

        super().__init__(
            index_name=index_name,
            api_token=api_token,
            space_type=space_type,
            dimension=dimension,
            insert_kwargs=insert_kwargs,
            add_sparse_vector=add_sparse_vector,
            text_key=text_key,
            batch_size=batch_size,
            remove_text_from_metadata=remove_text_from_metadata,
            vocab_size=vocab_size,
            hybrid=hybrid,
            model_name=model_name,
            precision=precision,
            key=key,
        )

        # Initialize index based on hybrid flag
        if endee_index is not None:
            # Use provided index
            self._endee_index = endee_index
        elif hybrid:
            # Initialize hybrid index
            self._endee_index = self._initialize_hybrid_index(
                api_token, index_name, dimension, space_type, vocab_size, precision, key
            )
        else:
            # Initialize regular index
            self._endee_index = self._initialize_endee_index(
                api_token, index_name, dimension, space_type, precision, key
            )

        # Initialize sparse encoder if model name is provided and hybrid mode is enabled
        if hybrid and model_name:
            _logger.info(f"Initializing sparse encoder with model: {model_name}")
            self._sparse_encoder = get_sparse_encoder(
                model_name=model_name,
                use_fastembed=True,  # Default to FastEmbed
                batch_size=batch_size,
            )
        else:
            self._sparse_encoder = None
       

    @classmethod
    def _initialize_endee_index(
        cls,
        api_token: Optional[str],
        index_name: Optional[str],
        dimension: Optional[int] = None,
        space_type: Optional[str] = "cosine",
        precision: Optional[str] = "medium",
        key: Optional[str] = None,
    ) -> Any:
        """Initialize Endee index using the current API."""
        endee = _import_endee()
        from endee.endee import Endee

        # Initialize Endee client
        nd = Endee(token=api_token)

        try:
            # Try to get existing index
            index = nd.get_index(name=index_name, key=key)
            _logger.info(f"Retrieved existing index: {index_name}")
            return index
        except Exception as e:
            if dimension is None:
                raise ValueError(
                    "Must provide dimension when creating a new index"
                ) from e
            
            # Create a new index if it doesn't exist
            _logger.info(f"Creating new index: {index_name}")
            nd.create_index(
                name=index_name,
                dimension=dimension,
                space_type=space_type,
                precision=precision,
                key=key,
            )
            return nd.get_index(name=index_name, key=key)

    @classmethod
    def _initialize_hybrid_index(
        cls,
        api_token: Optional[str],
        index_name: Optional[str],
        dimension: Optional[int] = None,
        space_type: Optional[str] = "cosine",
        vocab_size: Optional[int] = None,
        precision: Optional[str] = "medium",
        key: Optional[str] = None,
    ) -> Any:
        """Initialize Endee hybrid index using the current API."""
        endee = _import_endee()
        from endee.endee import Endee

        # Initialize Endee client
        nd = Endee(token=api_token)

        try:
            # Try to get existing hybrid index
            index = nd.get_hybrid_index(name=index_name, key=key)
            _logger.info(f"Retrieved existing hybrid index: {index_name}")
            return index
        except Exception as e:
            if dimension is None:
                raise ValueError(
                    "Must provide dimension when creating a new hybrid index"
                ) from e
            if vocab_size is None:
                raise ValueError(
                    "Must provide vocab_size when creating a new hybrid index"
                ) from e
            
            # Create a new hybrid index if it doesn't exist
            _logger.info(f"Creating new hybrid index: {index_name}")
            nd.create_hybrid_index(
                name=index_name,
                dimension=dimension,
                space_type=space_type,
                vocab_size=vocab_size,
                precision=precision,
                key=key,
            )
            return nd.get_hybrid_index(name=index_name, key=key)

    @classmethod
    def from_params(
        cls,
        api_token: Optional[str] = None,
        index_name: Optional[str] = None,
        dimension: Optional[int] = None,
        space_type: str = "cosine",
        batch_size: int = DEFAULT_BATCH_SIZE,
        hybrid: bool = False,
        vocab_size: Optional[int] = None,
        model_name: Optional[str] = None,
        precision: Optional[str] = "medium",
        key: Optional[str] = None,
    ) -> "EndeeVectorStore":
        """Create EndeeVectorStore from parameters.
        
        Args:
            api_token: API token for Endee service
            index_name: Name of the index
            dimension: Vector dimension
            space_type: Distance metric ("cosine", "l2", or "ip")
            batch_size: Batch size for operations
            hybrid: If True, create/use a hybrid index (supports both dense and sparse vectors)
            vocab_size: Vocabulary size for hybrid index (required if hybrid=True)
            model_name: Model name or alias for sparse embeddings (e.g., 'splade_pp', 'bert_base')
                       Supported models:
                       - 'splade_pp': prithivida/Splade_PP_en_v1 (~438 MB)
                       - 'splade_cocondenser': naver/splade-cocondenser-ensembledistil (~438 MB)
                       - 'bert_base': bert-base-uncased (~420 MB)
                       - 'distilbert': distilbert-base-uncased (~256 MB)
                       - 'minilm': sentence-transformers/all-MiniLM-L6-v2 (~90 MB)
                       - 'mpnet': sentence-transformers/all-mpnet-base-v2 (~420 MB)
                       - 'roberta': roberta-base (~501 MB)
                       - 'xlm_roberta': xlm-roberta-base (~1.3 GB)
            precision: Precision setting for index ("low", "medium", "high", or None)
            key: Encryption key for encrypting metadata (256-bit hex key, 64 hex characters)
                If provided, metadata will be encrypted using AES-256. Store this key securely.
        """
        if hybrid:
            endee_index = cls._initialize_hybrid_index(
                api_token, index_name, dimension, space_type, vocab_size, precision, key
            )
        else:
            endee_index = cls._initialize_endee_index(
                api_token, index_name, dimension, space_type, precision, key
            )

        return cls(
            endee_index=endee_index,
            api_token=api_token,
            index_name=index_name,
            dimension=dimension,
            space_type=space_type,
            batch_size=batch_size,
            vocab_size=vocab_size,
            hybrid=hybrid,
            model_name=model_name,
            precision=precision,
            key=key,
        )

    @classmethod
    def class_name(cls) -> str:
        return "EndeeVectorStore"

    def _compute_sparse_vectors(self, texts: List[str]) -> tuple:
        """Compute sparse vectors for a list of texts."""
        if self._sparse_encoder is None:
            raise ValueError(
                "Sparse encoder not initialized. "
                "Please provide model_name when creating the store with hybrid=True."
            )
        return self._sparse_encoder(texts)

    def add(
        self,
        nodes: List[BaseNode],
        hybrid: Optional[bool] = None,
        **add_kwargs: Any,
    ) -> List[str]:
        """
        Add nodes to index.

        Args:
            nodes: List[BaseNode]: list of nodes with embeddings
            hybrid: If True, compute and include sparse vectors for hybrid search.
                   Defaults to self.hybrid if not specified.
        """
        # Use instance hybrid setting if not explicitly provided
        use_hybrid = hybrid if hybrid is not None else self.hybrid
        
        ids = []
        entries = []
        texts = []
        
        # Collect texts for sparse encoding if hybrid mode
        if use_hybrid:
            for node in nodes:
                text = node.get_content()
                texts.append(text)
            
            # Compute sparse vectors in batch
            if self._sparse_encoder is not None and texts:
                sparse_indices, sparse_values = self._compute_sparse_vectors(texts)
            else:
                sparse_indices = [[] for _ in texts]
                sparse_values = [[] for _ in texts]
        
        for i, node in enumerate(nodes):
            node_id = node.node_id
            metadata = node_to_metadata_dict(node)
            
            # Filter values must be simple key-value pairs
            filter_data = {}
            if "file_name" in metadata:
                filter_data["file_name"] = metadata["file_name"]
            if "doc_id" in metadata:
                filter_data["doc_id"] = metadata["doc_id"]
            if "category" in metadata:
                filter_data["category"] = metadata["category"]
            if "difficulty" in metadata:
                filter_data["difficulty"] = metadata["difficulty"]
            if "language" in metadata:
                filter_data["language"] = metadata["language"]
            if "field" in metadata:
                filter_data["field"] = metadata["field"]
            if "type" in metadata:
                filter_data["type"] = metadata["type"]
            if "feature" in metadata:
                filter_data["feature"] = metadata["feature"]

            
            # Build entry based on hybrid mode
            if use_hybrid:
                entry = {
                    "id": node_id,
                    "dense_vector": node.get_embedding(),
                    "sparse_vector": {
                        "indices": sparse_indices[i],
                        "values": sparse_values[i]
                    },
                    "meta": metadata,
                }
            else:
                entry = {
                    "id": node_id,
                    "vector": node.get_embedding(),
                    "meta": metadata,
                    "filter": filter_data
                }

            ids.append(node_id)
            entries.append(entry)
        
        # Batch insert to avoid hitting API limits
        batch_size = self.batch_size
        for i in range(0, len(entries), batch_size):
            batch = entries[i : i + batch_size]
            self._endee_index.upsert(batch)
        
        return ids

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id.
        
        Args:
            ref_doc_id (str): The id of the document to delete.
        """
        try:
            self._endee_index.delete_with_filter({"doc_id": ref_doc_id})
        except Exception as e:
            _logger.error(f"Error deleting vectors for doc_id {ref_doc_id}: {e}")

    @property
    def client(self) -> Any:
        """Return Endee index client."""
        return self._endee_index
        

    def query(
        self,
        query: VectorStoreQuery,
        hybrid: Optional[bool] = None,
        sparse_query_text: Optional[str] = None,
        sparse_top_k: Optional[int] = None,
        dense_top_k: Optional[int] = None,
        rrf_k: int = 60,
        **kwargs: Any,
    ) -> VectorStoreQueryResult:
        """
        Query index for top k most similar nodes.

        Args:
            query: VectorStoreQuery object containing query parameters
            hybrid: If True, perform hybrid search with sparse vectors.
                   Defaults to self.hybrid if not specified.
            sparse_query_text: Text to compute sparse vector for query.
                              If not provided, uses query.query_str if available.
            sparse_top_k: Top K results from sparse search (for hybrid).
                         Defaults to query.similarity_top_k if not specified.
            dense_top_k: Top K results from dense search (for hybrid).
                        Defaults to query.similarity_top_k if not specified.
            rrf_k: Reciprocal Rank Fusion parameter (default: 60).
        """
        # Use instance hybrid setting if not explicitly provided
        use_hybrid = hybrid if hybrid is not None else self.hybrid
        
        if not hasattr(self._endee_index, 'dimension'):
            # Get dimension from index if available, otherwise try to infer from query
            try:
                dimension = self._endee_index.describe()["dimension"]
            except:
                if query.query_embedding is not None:
                    dimension = len(query.query_embedding)
                else:
                    raise ValueError("Could not determine vector dimension")
        else:
            dimension = self._endee_index.dimension
        
        query_embedding = [0.0] * dimension  # Default empty vector
        filters = {}

        # Apply any metadata filters if provided
        if query.filters is not None:
            for filter_item in query.filters.filters:
                # Case 1: MetadataFilter object
                if hasattr(filter_item, "key") and hasattr(filter_item, "value") and hasattr(filter_item, "operator"):
                    op_symbol = reverse_operator_map.get(filter_item.operator)
                    if not op_symbol:
                        raise ValueError(f"Unsupported filter operator: {filter_item.operator}")
                    
                    if filter_item.key not in filters:
                        filters[filter_item.key] = {}

                    filters[filter_item.key][op_symbol] = filter_item.value

                # Case 2: Raw dict, e.g. {"category": {"$eq": "programming"}}
                elif isinstance(filter_item, dict):
                    for key, op_dict in filter_item.items():
                        if isinstance(op_dict, dict):
                            for op, val in op_dict.items():
                                if key not in filters:
                                    filters[key] = {}
                                filters[key][op] = val
                else:
                    raise ValueError(f"Unsupported filter format: {filter_item}")

        _logger.info(f"Final structured filters: {filters}")

        # Use the query embedding if provided
        if query.query_embedding is not None:
            query_embedding = cast(List[float], query.query_embedding)
            if query.alpha is not None and query.mode == VectorStoreQueryMode.HYBRID:
                # Apply alpha scaling in hybrid mode
                query_embedding = [v * query.alpha for v in query_embedding]

        # Compute sparse query vector if hybrid mode
        sparse_vector = {"indices": [], "values": []}
        
        if use_hybrid:
            query_text = sparse_query_text or getattr(query, 'query_str', None)
            if query_text and self._sparse_encoder is not None:
                sparse_indices_batch, sparse_values_batch = self._compute_sparse_vectors([query_text])
                sparse_vector = {
                    "indices": sparse_indices_batch[0],
                    "values": sparse_values_batch[0]
                }

        # Set default top_k values for hybrid search
        use_sparse_top_k = sparse_top_k if sparse_top_k is not None else query.similarity_top_k
        use_dense_top_k = dense_top_k if dense_top_k is not None else query.similarity_top_k

        # Execute query
        try:
            if use_hybrid:
                # Hybrid search using RRF (Reciprocal Rank Fusion)
                results = self._endee_index.search(
                    dense_vector=query_embedding,
                    sparse_vector=sparse_vector,
                    sparse_top_k=use_sparse_top_k,
                    dense_top_k=use_dense_top_k,
                    include_vectors=True,
                    rrf_k=rrf_k,
                )
            else:
                # Regular dense query
                results = self._endee_index.query(
                    vector=query_embedding,
                    top_k=query.similarity_top_k,
                    filter=filters if filters else None,
                    include_vectors=True
                )
        except Exception as e:
            _logger.error(f"Error querying Endee: {e}")
            return VectorStoreQueryResult(nodes=[], similarities=[], ids=[])

        # Process results
        nodes = []
        similarities = []
        ids = []

        for result in results:
            node_id = result["id"]
            score = result.get("similarity", result.get("score", 0.0))
            
            # Get metadata from result
            metadata = result.get("meta", {})
            
            # Create node from metadata
            if self.flat_metadata:
                node = metadata_dict_to_node(
                    metadata=metadata,
                    text=metadata.pop(self.text_key, None),
                    id_=node_id,
                )
            else:
                metadata_dict, node_info, relationships = legacy_metadata_dict_to_node(
                    metadata=metadata,
                    text_key=self.text_key,
                )
                
                # Create TextNode with the extracted metadata
                # Step 1: Get the JSON string from "_node_content"
                _node_content_str = metadata.get("_node_content", "{}")

                # Step 2: Convert JSON string to Python dict
                try:
                    node_content = json.loads(_node_content_str)
                except json.JSONDecodeError:
                    node_content = {}

                # Step 3: Get the text
                text = node_content.get(self.text_key, "")
                node = TextNode(
                    text=text,
                    metadata=metadata_dict,
                    relationships=relationships,
                    node_id=node_id,
                )
                
                # Add any node_info properties to the node
                for key, val in node_info.items():
                    if hasattr(node, key):
                        setattr(node, key, val)
            
            # If embedding was returned in the results, add it to the node
            if "vector" in result:
                node.embedding = result["vector"]
            
            nodes.append(node)
            similarities.append(score)
            ids.append(node_id)

        return VectorStoreQueryResult(nodes=nodes, similarities=similarities, ids=ids)

        
