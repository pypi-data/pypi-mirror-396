# Endee LlamaIndex Integration

Build powerful RAG applications with Endee vector database and LlamaIndex.

---

## Table of Contents

1. [Installation](#1-installation)
2. [Setting up Credentials](#2-setting-up-endee-and-openai-credentials)
3. [Creating Sample Documents](#3-creating-sample-documents)
4. [Setting up Endee with LlamaIndex](#4-setting-up-endee-with-llamaindex)
5. [Creating a Vector Index](#5-creating-a-vector-index-from-documents)
6. [Basic Retrieval](#6-basic-retrieval-with-query-engine)
7. [Using Metadata Filters](#7-using-metadata-filters)
8. [Advanced Filtering](#8-advanced-filtering-with-multiple-conditions)
9. [Custom Retriever Setup](#9-custom-retriever-setup)
10. [Custom Retriever with Query Engine](#10-using-a-custom-retriever-with-a-query-engine)
11. [Direct VectorStore Querying](#11-direct-vectorstore-querying)
12. [Saving and Loading Indexes](#12-saving-and-loading-indexes)
13. [Cleanup](#13-cleanup)

---

## 1. Installation

Get started by installing the required package.

```bash
pip install endee-llamaindex
```

> **Note:** This will automatically install `endee` and `llama-index` as dependencies.

---

## 2. Setting up Endee and OpenAI credentials

Configure your API credentials for Endee and OpenAI.

```python
import os
from llama_index.embeddings.openai import OpenAIEmbedding

# Set API keys
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
endee_api_token = "your-endee-api-token"
```

> **Tip:** Store your API keys in environment variables for production use.

---

## 3. Creating Sample Documents

Create documents with metadata for filtering and organization.

```python
from llama_index.core import Document

# Create sample documents with different categories and metadata
documents = [
    Document(
        text="Python is a high-level, interpreted programming language known for its readability and simplicity.",
        metadata={"category": "programming", "language": "python", "difficulty": "beginner"}
    ),
    Document(
        text="JavaScript is a scripting language that enables interactive web pages and is an essential part of web applications.",
        metadata={"category": "programming", "language": "javascript", "difficulty": "intermediate"}
    ),
    Document(
        text="Machine learning is a subset of artificial intelligence that provides systems the ability to automatically learn and improve from experience.",
        metadata={"category": "ai", "field": "machine_learning", "difficulty": "advanced"}
    ),
    Document(
        text="Deep learning is part of a broader family of machine learning methods based on artificial neural networks with representation learning.",
        metadata={"category": "ai", "field": "deep_learning", "difficulty": "advanced"}
    ),
    Document(
        text="Vector databases are specialized database systems designed to store and query high-dimensional vectors for similarity search.",
        metadata={"category": "database", "type": "vector", "difficulty": "intermediate"}
    ),
    Document(
        text="Endee is a vector database that provides secure and private vector search capabilities.",
        metadata={"category": "database", "type": "vector", "product": "endee", "difficulty": "intermediate"}
    )
]

print(f"Created {len(documents)} sample documents")
```

**Output:**
```
Created 6 sample documents
```

---

## 4. Setting up Endee with LlamaIndex

Initialize the Endee vector store and connect it to LlamaIndex.

```python
from endee_llamaindex import EndeeVectorStore
from llama_index.core import StorageContext
import time

# Create a unique index name with timestamp to avoid conflicts
timestamp = int(time.time())
index_name = f"llamaindex_demo_{timestamp}"

# Set up the embedding model
embed_model = OpenAIEmbedding()

# Get the embedding dimension
dimension = 1536  # OpenAI's default embedding dimension

# Initialize the Endee vector store
vector_store = EndeeVectorStore.from_params(
    api_token=endee_api_token,
    index_name=index_name,
    dimension=dimension,
    space_type="cosine",  # Can be "cosine", "l2", or "ip"
    precision="medium"  # Index precision: "low", "medium", "high", or None
)

# Create storage context with our vector store
storage_context = StorageContext.from_defaults(vector_store=vector_store)

print(f"Initialized Endee vector store with index: {index_name}")
```

### Configuration Options

| Parameter | Description | Options |
|-----------|-------------|---------|
| `space_type` | Distance metric for similarity | `cosine`, `l2`, `ip` |
| `dimension` | Vector dimension | Must match embedding model |
| `precision` | Index precision setting | `"low"`, `"medium"` (default), `"high"`, or `None` |
| `key` | Encryption key for metadata | 256-bit hex key (64 hex characters) |
| `batch_size` | Vectors per API call | Default: `100` |

---

## 5. Creating a Vector Index from Documents

Build a searchable vector index from your documents.

```python
from llama_index.core import VectorStoreIndex

# Create a vector index
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    embed_model=embed_model
)

print("Vector index created successfully")
```

**Output:**
```
Vector index created successfully
```

---

## 6. Basic Retrieval with Query Engine

Create a query engine and perform semantic search.

```python
# Create a query engine
query_engine = index.as_query_engine()

# Ask a question
response = query_engine.query("What is Python?")

print("Query: What is Python?")
print("Response:")
print(response)
```

**Example Output:**
```
Query: What is Python?
Response:
Python is a high-level, interpreted programming language known for its readability and simplicity.
```

---

## 7. Using Metadata Filters

Filter search results based on document metadata.

```python
from llama_index.core.vector_stores.types import MetadataFilters, MetadataFilter, FilterOperator

# Create a filtered retriever to only search within AI-related documents
ai_filter = MetadataFilter(key="category", value="ai", operator=FilterOperator.EQ)
ai_filters = MetadataFilters(filters=[ai_filter])

# Create a filtered query engine
filtered_query_engine = index.as_query_engine(filters=ai_filters)

# Ask a general question but only using AI documents
response = filtered_query_engine.query("What is learning from data?")

print("Filtered Query (AI category only): What is learning from data?")
print("Response:")
print(response)
```

### Available Filter Operators

| Operator | Description |
|----------|-------------|
| `FilterOperator.EQ` | Equal to |
| `FilterOperator.NE` | Not equal to |
| `FilterOperator.GT` | Greater than |
| `FilterOperator.GTE` | Greater than or equal |
| `FilterOperator.LT` | Less than |
| `FilterOperator.LTE` | Less than or equal |
| `FilterOperator.IN` | In list |
| `FilterOperator.NIN` | Not in list |

---

## 8. Advanced Filtering with Multiple Conditions

Combine multiple metadata filters for precise results.

```python
# Create a more complex filter: database category AND intermediate difficulty
category_filter = MetadataFilter(key="category", value="database", operator=FilterOperator.EQ)
difficulty_filter = MetadataFilter(key="difficulty", value="intermediate", operator=FilterOperator.EQ)

complex_filters = MetadataFilters(filters=[category_filter, difficulty_filter])

# Create a query engine with the complex filters
complex_filtered_engine = index.as_query_engine(filters=complex_filters)

# Query with the complex filters
response = complex_filtered_engine.query("Tell me about databases")

print("Complex Filtered Query (database category AND intermediate difficulty): Tell me about databases")
print("Response:")
print(response)
```

> **Note:** Multiple filters are combined with AND logic by default.

---

## 9. Custom Retriever Setup

Create a custom retriever for fine-grained control over the retrieval process.

```python
from llama_index.core.retrievers import VectorIndexRetriever

# Create a retriever with custom parameters
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=3,  # Return top 3 most similar results
    filters=ai_filters   # Use our AI category filter from before
)

# Retrieve nodes for a query
nodes = retriever.retrieve("What is deep learning?")

print(f"Retrieved {len(nodes)} nodes for query: 'What is deep learning?' (with AI category filter)")
print("\nRetrieved content:")
for i, node in enumerate(nodes):
    print(f"\nNode {i+1}:")
    print(f"Text: {node.node.text}")
    print(f"Metadata: {node.node.metadata}")
    print(f"Score: {node.score:.4f}")
```

**Example Output:**
```
Retrieved 2 nodes for query: 'What is deep learning?' (with AI category filter)

Node 1:
Text: Deep learning is part of a broader family of machine learning methods...
Metadata: {'category': 'ai', 'field': 'deep_learning', 'difficulty': 'advanced'}
Score: 0.8934

Node 2:
Text: Machine learning is a subset of artificial intelligence...
Metadata: {'category': 'ai', 'field': 'machine_learning', 'difficulty': 'advanced'}
Score: 0.7821
```

---

## 10. Using a Custom Retriever with a Query Engine

Combine your custom retriever with a query engine for enhanced control.

```python
from llama_index.core.query_engine import RetrieverQueryEngine

# Create a query engine with our custom retriever
custom_query_engine = RetrieverQueryEngine.from_args(
    retriever=retriever,
    verbose=True  # Enable verbose mode to see the retrieved nodes
)

# Query using the custom retriever query engine
response = custom_query_engine.query("Explain the difference between machine learning and deep learning")

print("\nFinal Response:")
print(response)
```

---

## 11. Direct VectorStore Querying

Query the Endee vector store directly, bypassing the LlamaIndex query engine.

```python
from llama_index.core.vector_stores.types import VectorStoreQuery

# Generate an embedding for our query
query_text = "What are vector databases?"
query_embedding = embed_model.get_text_embedding(query_text)

# Create a VectorStoreQuery
vector_store_query = VectorStoreQuery(
    query_embedding=query_embedding,
    similarity_top_k=2,
    filters=MetadataFilters(filters=[MetadataFilter(key="category", value="database", operator=FilterOperator.EQ)])
)

# Execute the query directly on the vector store
query_result = vector_store.query(vector_store_query)

print(f"Direct VectorStore query: '{query_text}'")
print(f"Retrieved {len(query_result.nodes)} results with database category filter:")
for i, (node, score) in enumerate(zip(query_result.nodes, query_result.similarities)):
    print(f"\nResult {i+1}:")
    print(f"Text: {node.text}")
    print(f"Metadata: {node.metadata}")
    print(f"Similarity score: {score:.4f}")
```

> **Tip:** Direct querying is useful when you need raw results without LLM processing.

---

## 12. Saving and Loading Indexes

Reconnect to your index in future sessions. Your vectors are stored in the cloud.

```python
# To reconnect to an existing index in a future session:
def reconnect_to_index(api_token, index_name):
    # Initialize the vector store with existing index
    vector_store = EndeeVectorStore.from_params(
        api_token=api_token,
        index_name=index_name
    )
    
    # Create storage context
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Load the index
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=OpenAIEmbedding()
    )
    
    return index

# Example usage
reconnected_index = reconnect_to_index(endee_api_token, index_name)
query_engine = reconnected_index.as_query_engine()
response = query_engine.query("What is Endee?")
print(response)

print(f"To reconnect to this index in the future, use:\n")
print(f"API Token: {endee_api_token}")
print(f"Index Name: {index_name}")
```

> **Important:** Save your `index_name` to reconnect to your data later.

---

## 13. Cleanup

Delete the index when you're done to free up resources.

```python
# Uncomment to delete your index
# endee.delete_index(index_name)
# print(f"Index {index_name} deleted")
```

> **Warning:** Deleting an index permanently removes all stored vectors and cannot be undone.

---

## Quick Reference

### EndeeVectorStore Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `api_token` | `str` | Your Endee API token | Required |
| `index_name` | `str` | Name of the index | Required |
| `dimension` | `int` | Vector dimension | Required |
| `space_type` | `str` | Distance metric | `"cosine"` |
| `precision` | `str` | Index precision setting | `"medium"` |
| `key` | `str` | Encryption key for metadata (256-bit hex) | `None` |
| `batch_size` | `int` | Vectors per API call | `100` |

### Distance Metrics

| Metric | Best For |
|--------|----------|
| `cosine` | Text embeddings, normalized vectors |
| `l2` | Image features, spatial data |
| `ip` | Recommendation systems, dot product similarity |

### Precision Settings

The `precision` parameter controls the trade-off between search accuracy and performance:

| Precision | Description | Use Case |
|-----------|-------------|----------|
| `"low"` | Faster searches, lower accuracy | Large-scale applications where speed is critical |
| `"medium"` | Balanced performance and accuracy | General purpose applications (default) |
| `"high"` | Slower searches, higher accuracy | Applications requiring maximum precision |
| `None` | Default system precision | Use system defaults |

### Encryption Support

You can encrypt metadata stored in Endee by providing a 256-bit encryption key (64 hex characters). This ensures sensitive information is encrypted at rest.

```python
# Generate a 256-bit key (example - use a secure method in production)
import secrets
encryption_key = secrets.token_hex(32)  # 32 bytes = 64 hex characters

# Create vector store with encryption
vector_store = EndeeVectorStore.from_params(
    api_token=endee_api_token,
    index_name=index_name,
    dimension=dimension,
    space_type="cosine",
    precision="medium",
    key=encryption_key  # Metadata will be encrypted
)

# Important: Store this key securely! You'll need it to access the index later.
```

> **Warning:** If you lose the encryption key, you will not be able to decrypt your metadata. Store it securely (e.g., in a secrets manager).

---


