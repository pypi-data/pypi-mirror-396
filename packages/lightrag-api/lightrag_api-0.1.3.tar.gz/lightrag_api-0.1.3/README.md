# 🚀 lightrag-api

Simple LightRAG API client for Python.

This library provides both synchronous and asynchronous clients for interacting with the LightRAG API, enabling document management, RAG queries, knowledge graph operations, and more.

## 📦 Installation

Install from source using `uv` or `pip`:

```bash
# Using uv
uv add lightrag-api

# Using pip
pip install lightrag-api
```

**Requirements:**
- 🐍 Python >= 3.10
- 📡 httpx >= 0.28.1
- ✅ pydantic >= 2.12.5

## ⚡ Quick Start

### Synchronous Client

```python
from lightrag.api import SyncLightRagClient

# Initialize client with API key
client = SyncLightRagClient(
    base_url="https://your-lightrag-server.com",
    api_key="your-api-key"
)

# Execute a query
response = client.query("What is machine learning?")
print(response.response)

# Don't forget to close the client
client.close()
```

### Asynchronous Client

```python
from lightrag.api import AsyncLightRagClient

async def main():
    # Initialize client with OAuth token
    client = AsyncLightRagClient(
        base_url="https://your-lightrag-server.com",
        oauth_token="your-oauth-token"
    )
    
    try:
        # Execute a query
        response = await client.query("What is machine learning?")
        print(response.response)
    finally:
        await client.close()

# Run the async function
import asyncio
asyncio.run(main())
```

## ✨ Features

- 📄 **Document Management**: Upload documents, insert text, delete documents, and manage document pipelines
- 🔍 **RAG Queries**: Execute queries with multiple modes (local, global, hybrid, naive, mix, bypass), streaming support, and conversation history
- 🕸️ **Knowledge Graph Operations**: Create, update, merge, and delete entities and relations
- ⚙️ **Pipeline Management**: Monitor and control document processing pipelines
- 🔄 **Dual Client Support**: Both synchronous (`SyncLightRagClient`) and asynchronous (`AsyncLightRagClient`) clients
- 🛡️ **Type Safety**: Full Pydantic model support for request/response validation

## 💡 Usage Examples

### 🔧 Initialize Client

```python
from lightrag.api import SyncLightRagClient, AsyncLightRagClient

# Sync client with API key
sync_client = SyncLightRagClient(
    base_url="https://api.example.com",
    api_key="your-api-key"
)

# Async client with OAuth token
async_client = AsyncLightRagClient(
    base_url="https://api.example.com",
    oauth_token="your-oauth-token"
)
```

### ❓ Simple Query

```python
# Synchronous query
response = sync_client.query(
    query="Explain quantum computing",
    mode="mix",
    include_references=True
)
print(response.response)
print(response.references)

# Asynchronous query
response = await async_client.query(
    query="Explain quantum computing",
    mode="mix",
    include_references=True
)
```

### 📤 Upload Document

```python
# Upload a file
response = sync_client.upload_document("path/to/document.pdf")
print(f"Document ID: {response.doc_id}")

# Or upload from bytes
with open("document.pdf", "rb") as f:
    response = sync_client.upload_document(f.read())
```

### 📝 Insert Text

```python
# Insert single text
response = sync_client.insert_text(
    text="Your document content here...",
    file_source="manual_input.txt"
)

# Insert multiple texts
response = sync_client.insert_texts(
    texts=["Text 1", "Text 2", "Text 3"],
    file_sources=["doc1.txt", "doc2.txt", "doc3.txt"]
)
```

## 📚 API Overview

### 📄 Document Management

- `upload_document(file)` - Upload a document file
- `insert_text(text, file_source)` - Insert text into the system
- `insert_texts(texts, file_sources)` - Insert multiple texts
- `get_documents()` - Get statuses of all documents
- `get_documents_paginated(page, page_size)` - Get paginated document list
- `delete_document(doc_ids, delete_file, delete_llm_cache)` - Delete documents by ID
- `clear_documents()` - Clear all documents
- `get_pipeline_status()` - Get document processing pipeline status
- `cancel_pipeline()` - Cancel current processing pipeline
- `reprocess_failed()` - Reprocess failed documents
- `get_status_counts()` - Get document status counts
- `get_track_status(track_id)` - Track document processing status
- `scan_documents()` - Scan for new documents

### 🔍 Query Methods

- `query(query, mode, include_references, ...)` - Execute RAG query
- `query_stream(query, mode, ...)` - Execute streaming RAG query
- `query_data(query, mode, ...)` - Execute query and return structured data

### 🕸️ Knowledge Graph Operations

- `create_entity(name, description, labels)` - Create a new entity
- `update_entity(name, description, labels)` - Update an existing entity
- `delete_entity(entity_name)` - Delete an entity
- `merge_entities(source_name, target_name)` - Merge two entities
- `create_relation(source, target, relation, description)` - Create a relation
- `update_relation(source, target, relation, description)` - Update a relation
- `delete_relation(source, target, relation)` - Delete a relation
- `get_knowledge_graph(limit)` - Get knowledge graph data
- `get_graph_labels()` - Get all graph labels
- `get_popular_labels(limit)` - Get popular labels
- `search_labels(q, limit)` - Search labels
- `check_entity_exists(name)` - Check if entity exists

### 🛠️ Utility Methods

- `clear_cache()` - Clear LLM response cache
- `get_version()` - Get API version
- `get_tags()` - Get available tags
- `get_running_models()` - Get running models
- `get_health()` - Check API health status
- `get_auth_status()` - Get authentication status
- `login(username, password)` - Login and get token
- `generate(**kwargs)` - Generate text
- `chat(**kwargs)` - Chat with the API

For detailed method signatures and parameters, refer to the source code documentation in `src/lightrag/api/_sync_client.py` and `src/lightrag/api/_async_client.py`.

## 🔐 Authentication

The client supports two authentication methods:

### 🔑 API Key Authentication

```python
client = SyncLightRagClient(
    base_url="https://api.example.com",
    api_key="your-api-key"
)
```

The API key is sent in the `X-API-Key` header.

### 🎫 OAuth Token Authentication

```python
client = SyncLightRagClient(
    base_url="https://api.example.com",
    oauth_token="your-oauth-token"
)
```

The OAuth token is sent in the `Authorization: Bearer` header.

**Note:** ⚠️ If both are provided, OAuth token takes priority.

## ⚠️ Error Handling

The library provides two exception types:

- `LightRagError` - Base exception for all LightRAG API errors
- `LightRagHttpError` - Exception for HTTP-related errors

```python
from lightrag.api import SyncLightRagClient, LightRagError, LightRagHttpError

client = SyncLightRagClient(base_url="https://api.example.com", api_key="key")

try:
    response = client.query("test query")
except LightRagHttpError as e:
    print(f"HTTP error occurred: {e}")
except LightRagError as e:
    print(f"LightRAG error occurred: {e}")
```

## 🔗 Links

- 📖 [LightRAG Documentation](https://github.com/HKUDS/LightRAG) - Official LightRAG project documentation

## ❓ FAQ

> Why do you write code manually? There is an `openapi-python-client` generator.

`openapi-python-client` generates slop client code.
