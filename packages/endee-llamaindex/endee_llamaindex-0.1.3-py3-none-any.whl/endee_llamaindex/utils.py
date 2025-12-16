import logging
from collections import Counter
from typing import Any, Callable, Dict, List, Optional, cast
import json

from llama_index.core.bridge.pydantic import PrivateAttr
from llama_index.core.schema import BaseNode, TextNode
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
from llama_index.core.vector_stores.types import MetadataFilter, FilterOperator

_logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 100

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


def _import_endee() -> Any:
    """Import endee module."""
    try:
        import endee
        from endee.endee import Endee
    except ImportError as e:
        raise ImportError(
            "Could not import endee python package. "
            "Please install it with `pip install endee`."
        ) from e
    return endee


def build_dict(input_batch: List[List[int]]) -> List[Dict[str, Any]]:
    """
    Build a list of sparse dictionaries from a batch of input_ids.
    """
    sparse_emb = []
    for token_ids in input_batch:
        indices = []
        values = []
        d = dict(Counter(token_ids))
        for idx in d:
            indices.append(idx)
            values.append(float(d[idx]))
        sparse_emb.append({"indices": indices, "values": values})
    return sparse_emb


def generate_sparse_vectors(
    context_batch: List[str], tokenizer: Callable
) -> List[Dict[str, Any]]:
    """Generate sparse vectors from a batch of contexts."""
    inputs = tokenizer(context_batch)["input_ids"]
    return build_dict(inputs)


def _initialize_sparse_encoder_fastembed(
    model_name: str,
    batch_size: int = 256,
    cache_dir: Optional[str] = None,
    threads: Optional[int] = None,
) -> Callable:
    """
    Initialize a sparse encoder using FastEmbed (recommended for SPLADE models).
    """
    try:
        from fastembed.sparse.sparse_text_embedding import SparseTextEmbedding
    except ImportError as e:
        raise ImportError(
            "Could not import FastEmbed. "
            "Please install it with `pip install fastembed` or "
            "`pip install fastembed-gpu` for GPU support."
        ) from e

    resolved_model_name = SUPPORTED_SPARSE_MODELS.get(model_name, model_name)
    
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


def _initialize_sparse_encoder_transformers(model_name: str) -> Callable:
    """
    Initialize a sparse encoder using Transformers library.
    """
    try:
        import torch
        from transformers import AutoModelForMaskedLM, AutoTokenizer
    except ImportError as e:
        raise ImportError(
            "Could not import transformers library. "
            'Please install transformers with `pip install "transformers[torch]"`'
        ) from e

    resolved_model_name = SUPPORTED_SPARSE_MODELS.get(model_name, model_name)
    
    tokenizer = AutoTokenizer.from_pretrained(resolved_model_name)
    model = AutoModelForMaskedLM.from_pretrained(resolved_model_name)
    
    if torch.cuda.is_available():
        model = model.to("cuda")
        _logger.info(f"Initialized sparse encoder '{resolved_model_name}' on GPU")
    else:
        _logger.info(f"Initialized sparse encoder '{resolved_model_name}' on CPU")

    def compute_vectors(texts: List[str]) -> tuple:
        """Compute sparse vectors from logits."""
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


class EndeeHybridVectorStore(BasePydanticVectorStore):
    """
    Endee Hybrid Vector Store for combined dense and sparse vector search.
    
    This class provides hybrid search capabilities using both dense embeddings
    and sparse vectors (e.g., SPLADE, BM25-style) for improved retrieval.
    """

    stores_text: bool = True
    flat_metadata: bool = False

    api_token: Optional[str]
    index_name: Optional[str]
    space_type: Optional[str]
    dimension: Optional[int]
    vocab_size: int
    insert_kwargs: Optional[Dict]
    text_key: str
    batch_size: int
    remove_text_from_metadata: bool
    model_name: Optional[str]
    use_fastembed: bool
    alpha: float  # Weight for dense vs sparse (0=sparse only, 1=dense only)

    _endee_index: Any = PrivateAttr()
    _sparse_encoder: Optional[Callable] = PrivateAttr(default=None)

    def __init__(
        self,
        endee_index: Optional[Any] = None,
        api_token: Optional[str] = None,
        index_name: Optional[str] = None,
        space_type: Optional[str] = "cosine",
        dimension: Optional[int] = None,
        vocab_size: int = 30522,  # Default BERT vocab size
        insert_kwargs: Optional[Dict] = None,
        text_key: str = DEFAULT_TEXT_KEY,
        batch_size: int = DEFAULT_BATCH_SIZE,
        remove_text_from_metadata: bool = False,
        model_name: Optional[str] = "splade_pp",
        use_fastembed: bool = True,
        alpha: float = 0.5,
        **kwargs: Any,
    ) -> None:
        insert_kwargs = insert_kwargs or {}

        super().__init__(
            index_name=index_name,
            api_token=api_token,
            space_type=space_type,
            dimension=dimension,
            vocab_size=vocab_size,
            insert_kwargs=insert_kwargs,
            text_key=text_key,
            batch_size=batch_size,
            remove_text_from_metadata=remove_text_from_metadata,
            model_name=model_name,
            use_fastembed=use_fastembed,
            alpha=alpha,
        )

        # Initialize hybrid index
        if endee_index is not None:
            self._endee_index = endee_index
        else:
            self._endee_index = self._initialize_hybrid_index(
                api_token, index_name, dimension, space_type, vocab_size
            )

        # Initialize sparse encoder
        if model_name:
            _logger.info(f"Initializing sparse encoder with model: {model_name}")
            self._sparse_encoder = get_sparse_encoder(
                model_name=model_name,
                use_fastembed=use_fastembed,
                batch_size=batch_size,
            )
        else:
            self._sparse_encoder = None

    @classmethod
    def _initialize_hybrid_index(
        cls,
        api_token: Optional[str],
        index_name: Optional[str],
        dimension: Optional[int] = None,
        space_type: Optional[str] = "cosine",
        vocab_size: Optional[int] = None,
    ) -> Any:
        """Initialize Endee hybrid index."""
        _import_endee()
        from endee.endee import Endee

        nd = Endee(token=api_token)

        try:
            index = nd.get_hybrid_index(name=index_name)
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
            
            _logger.info(f"Creating new hybrid index: {index_name}")
            nd.create_hybrid_index(
                name=index_name,
                dimension=dimension,
                space_type=space_type,
                vocab_size=vocab_size,
            )
            return nd.get_hybrid_index(name=index_name)

    @classmethod
    def from_params(
        cls,
        api_token: Optional[str] = None,
        index_name: Optional[str] = None,
        dimension: Optional[int] = None,
        space_type: str = "cosine",
        vocab_size: int = 30522,
        batch_size: int = DEFAULT_BATCH_SIZE,
        model_name: Optional[str] = "splade_pp",
        use_fastembed: bool = True,
        alpha: float = 0.5,
    ) -> "EndeeHybridVectorStore":
        """
        Create EndeeHybridVectorStore from parameters.
        
        Args:
            api_token: API token for Endee service
            index_name: Name of the hybrid index
            dimension: Vector dimension for dense embeddings
            space_type: Distance metric ("cosine", "l2", or "ip")
            vocab_size: Vocabulary size for sparse vectors
            batch_size: Batch size for operations
            model_name: Model name or alias for sparse embeddings
                       Supported models:
                       - 'splade_pp': prithivida/Splade_PP_en_v1
                       - 'splade_cocondenser': naver/splade-cocondenser-ensembledistil
                       - 'bert_base': bert-base-uncased
                       - 'distilbert': distilbert-base-uncased
                       - 'minilm': sentence-transformers/all-MiniLM-L6-v2
                       - 'mpnet': sentence-transformers/all-mpnet-base-v2
                       - 'roberta': roberta-base
                       - 'xlm_roberta': xlm-roberta-base
            use_fastembed: Use FastEmbed for sparse encoding (recommended)
            alpha: Weight for hybrid search (0=sparse only, 1=dense only, 0.5=balanced)
        """
        endee_index = cls._initialize_hybrid_index(
            api_token, index_name, dimension, space_type, vocab_size
        )

        return cls(
            endee_index=endee_index,
            api_token=api_token,
            index_name=index_name,
            dimension=dimension,
            space_type=space_type,
            vocab_size=vocab_size,
            batch_size=batch_size,
            model_name=model_name,
            use_fastembed=use_fastembed,
            alpha=alpha,
        )

    @classmethod
    def class_name(cls) -> str:
        return "EndeeHybridVectorStore"

    def _compute_sparse_vectors(self, texts: List[str]) -> tuple:
        """Compute sparse vectors for a list of texts."""
        if self._sparse_encoder is None:
            raise ValueError(
                "Sparse encoder not initialized. "
                "Please provide model_name when creating the store."
            )
        return self._sparse_encoder(texts)

    def add(
        self,
        nodes: List[BaseNode],
        **add_kwargs: Any,
    ) -> List[str]:
        """
        Add nodes to hybrid index with both dense and sparse vectors.

        Args:
            nodes: List[BaseNode]: list of nodes with embeddings
        """
        ids = []
        entries = []
        texts = []
        
        # Collect all texts for batch sparse encoding
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
            
            # Filter values for hybrid index
            filter_data = {}
            for key in ["file_name", "doc_id", "category", "difficulty", 
                        "language", "field", "type", "feature"]:
                if key in metadata:
                    filter_data[key] = metadata[key]
            
            entry = {
                "id": node_id,
                "vector": node.get_embedding(),
                "sparse_indices": sparse_indices[i],
                "sparse_values": sparse_values[i],
                "meta": metadata,
                "filter": filter_data
            }

            ids.append(node_id)
            entries.append(entry)
        
        # Batch upsert
        batch_size = self.batch_size
        for i in range(0, len(entries), batch_size):
            batch = entries[i : i + batch_size]
            self._endee_index.upsert(batch)
        
        return ids

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using ref_doc_id.
        
        Args:
            ref_doc_id (str): The id of the document to delete.
        """
        try:
            self._endee_index.delete_with_filter({"doc_id": ref_doc_id})
        except Exception as e:
            _logger.error(f"Error deleting vectors for doc_id {ref_doc_id}: {e}")

    def delete_by_ids(self, ids: List[str], **delete_kwargs: Any) -> None:
        """
        Delete nodes by their IDs.
        
        Args:
            ids: List of node IDs to delete.
        """
        try:
            self._endee_index.delete(ids)
        except Exception as e:
            _logger.error(f"Error deleting vectors by IDs: {e}")

    def delete_with_filter(self, filter_dict: Dict[str, Any], **delete_kwargs: Any) -> None:
        """
        Delete nodes matching a filter.
        
        Args:
            filter_dict: Filter dictionary for deletion.
        """
        try:
            self._endee_index.delete_with_filter(filter_dict)
        except Exception as e:
            _logger.error(f"Error deleting vectors with filter: {e}")

    @property
    def client(self) -> Any:
        """Return Endee hybrid index client."""
        return self._endee_index

    def query(
        self,
        query: VectorStoreQuery,
        sparse_query_text: Optional[str] = None,
        alpha: Optional[float] = None,
        **kwargs: Any,
    ) -> VectorStoreQueryResult:
        """
        Query hybrid index for top k most similar nodes.

        Args:
            query: VectorStoreQuery object containing query parameters
            sparse_query_text: Optional text to compute sparse vector for query.
                              If not provided, uses query.query_str if available.
            alpha: Optional weight override for this query (0=sparse only, 1=dense only)
        """
        # Get dimension
        try:
            dimension = self._endee_index.describe()["dimension"]
        except:
            if query.query_embedding is not None:
                dimension = len(query.query_embedding)
            else:
                raise ValueError("Could not determine vector dimension")
        
        query_embedding = [0.0] * dimension
        filters = {}
        use_alpha = alpha if alpha is not None else self.alpha

        # Build filters
        if query.filters is not None:
            for filter_item in query.filters.filters:
                if hasattr(filter_item, "key") and hasattr(filter_item, "value") and hasattr(filter_item, "operator"):
                    op_symbol = reverse_operator_map.get(filter_item.operator)
                    if not op_symbol:
                        raise ValueError(f"Unsupported filter operator: {filter_item.operator}")
                    
                    if filter_item.key not in filters:
                        filters[filter_item.key] = {}
                    filters[filter_item.key][op_symbol] = filter_item.value

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

        # Get dense query embedding
        if query.query_embedding is not None:
            query_embedding = cast(List[float], query.query_embedding)

        # Compute sparse query vector
        sparse_indices = []
        sparse_values = []
        
        query_text = sparse_query_text or getattr(query, 'query_str', None)
        if query_text and self._sparse_encoder is not None:
            sparse_indices_batch, sparse_values_batch = self._compute_sparse_vectors([query_text])
            sparse_indices = sparse_indices_batch[0]
            sparse_values = sparse_values_batch[0]

        # Execute hybrid query
        try:
            results = self._endee_index.query(
                vector=query_embedding,
                sparse_indices=sparse_indices,
                sparse_values=sparse_values,
                top_k=query.similarity_top_k,
                filter=filters if filters else None,
                include_vectors=True,
                alpha=use_alpha,
            )
        except Exception as e:
            _logger.error(f"Error querying Endee hybrid index: {e}")
            return VectorStoreQueryResult(nodes=[], similarities=[], ids=[])

        # Process results
        nodes = []
        similarities = []
        ids = []

        for result in results:
            node_id = result["id"]
            score = result.get("similarity", result.get("score", 0.0))
            metadata = result.get("meta", {})
            
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
                
                _node_content_str = metadata.get("_node_content", "{}")
                try:
                    node_content = json.loads(_node_content_str)
                except json.JSONDecodeError:
                    node_content = {}

                text = node_content.get(self.text_key, "")
                node = TextNode(
                    text=text,
                    metadata=metadata_dict,
                    relationships=relationships,
                    node_id=node_id,
                )
                
                for key, val in node_info.items():
                    if hasattr(node, key):
                        setattr(node, key, val)
            
            if "vector" in result:
                node.embedding = result["vector"]
            
            nodes.append(node)
            similarities.append(score)
            ids.append(node_id)

        return VectorStoreQueryResult(nodes=nodes, similarities=similarities, ids=ids)

    def hybrid_query(
        self,
        query_text: str,
        query_embedding: List[float],
        top_k: int = 10,
        alpha: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> VectorStoreQueryResult:
        """
        Direct hybrid query method for convenience.
        
        Args:
            query_text: Text query for sparse vector computation
            query_embedding: Dense embedding vector
            top_k: Number of results to return
            alpha: Weight for hybrid search (0=sparse, 1=dense)
            filters: Optional filter dictionary
        
        Returns:
            VectorStoreQueryResult with combined results
        """
        use_alpha = alpha if alpha is not None else self.alpha
        
        # Compute sparse vector
        sparse_indices = []
        sparse_values = []
        if self._sparse_encoder is not None:
            sparse_indices_batch, sparse_values_batch = self._compute_sparse_vectors([query_text])
            sparse_indices = sparse_indices_batch[0]
            sparse_values = sparse_values_batch[0]
        
        try:
            results = self._endee_index.query(
                vector=query_embedding,
                sparse_indices=sparse_indices,
                sparse_values=sparse_values,
                top_k=top_k,
                filter=filters,
                include_vectors=True,
                alpha=use_alpha,
            )
        except Exception as e:
            _logger.error(f"Error in hybrid query: {e}")
            return VectorStoreQueryResult(nodes=[], similarities=[], ids=[])

        nodes = []
        similarities = []
        ids = []

        for result in results:
            node_id = result["id"]
            score = result.get("similarity", result.get("score", 0.0))
            metadata = result.get("meta", {})
            
            metadata_dict, node_info, relationships = legacy_metadata_dict_to_node(
                metadata=metadata,
                text_key=self.text_key,
            )
            
            _node_content_str = metadata.get("_node_content", "{}")
            try:
                node_content = json.loads(_node_content_str)
            except json.JSONDecodeError:
                node_content = {}

            text = node_content.get(self.text_key, "")
            node = TextNode(
                text=text,
                metadata=metadata_dict,
                relationships=relationships,
                node_id=node_id,
            )
            
            for key, val in node_info.items():
                if hasattr(node, key):
                    setattr(node, key, val)
            
            if "vector" in result:
                node.embedding = result["vector"]
            
            nodes.append(node)
            similarities.append(score)
            ids.append(node_id)

        return VectorStoreQueryResult(nodes=nodes, similarities=similarities, ids=ids)

    def describe(self) -> Dict[str, Any]:
        """Get index description/stats."""
        try:
            return self._endee_index.describe()
        except Exception as e:
            _logger.error(f"Error describing index: {e}")
            return {}

    def list_ids(self, limit: int = 100) -> List[str]:
        """List IDs in the index."""
        try:
            return self._endee_index.list_ids(limit=limit)
        except Exception as e:
            _logger.error(f"Error listing IDs: {e}")
            return []

    def fetch(self, ids: List[str]) -> List[Dict[str, Any]]:
        """Fetch vectors by IDs."""
        try:
            return self._endee_index.fetch(ids)
        except Exception as e:
            _logger.error(f"Error fetching vectors: {e}")
            return []

