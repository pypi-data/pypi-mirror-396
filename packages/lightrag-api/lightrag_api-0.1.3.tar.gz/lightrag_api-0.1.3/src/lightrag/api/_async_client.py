import io
import json
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any, Literal

from httpx import AsyncClient, Response, Timeout

from lightrag.api._schemas import (
    CancelPipelineResponse,
    ClearCacheRequest,
    ClearCacheResponse,
    ClearDocumentsResponse,
    DeleteDocByIdResponse,
    DeleteDocRequest,
    DeleteEntityRequest,
    DeleteRelationRequest,
    DeletionResult,
    DocsStatusesResponse,
    DocumentsRequest,
    EntityCreateRequest,
    EntityMergeRequest,
    EntityUpdateRequest,
    InsertResponse,
    InsertTextRequest,
    InsertTextsRequest,
    PaginatedDocsResponse,
    PipelineStatusResponse,
    QueryDataResponse,
    QueryRequest,
    QueryResponse,
    RelationCreateRequest,
    RelationUpdateRequest,
    ReprocessResponse,
    ScanResponse,
    StatusCountsResponse,
    TrackStatusResponse,
)

from ._exceptions import LightRagError, LightRagHttpError


class AsyncLightRagClient:
    """
    Asynchronous HTTP client for LightRAG API.

    Provides convenient methods for working with all API endpoints.
    """

    def __init__(  # noqa: PLR0913
        self,
        base_url: str,
        api_key: str | None = None,
        oauth_token: str | None = None,
        async_client: AsyncClient | None = None,
        client_timeout: float | None = None,
        verify_ssl: str | bool | None = None,
    ):
        """
        Initialize the client.

        Args:
            base_url: Base URL of the API server
            api_key: API key for authentication (X-API-Key)
            oauth_token: OAuth2 token for authentication (Authorization: Bearer)
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.oauth_token = oauth_token

        if async_client is not None:
            self._client = async_client
        else:
            self._client = AsyncClient(
                base_url=base_url,
                timeout=Timeout(client_timeout),
                headers=self._get_headers(),
                verify=verify_ssl or False,
            )

    def _get_headers(self) -> dict[str, str]:
        """
        Get authentication headers.

        Priority: OAuth2 > API Key

        Returns:
            Dictionary with headers
        """
        headers = {}
        if self.oauth_token:
            headers["Authorization"] = f"Bearer {self.oauth_token}"
        elif self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    async def close(self):
        """Close the client and release resources."""
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        requires_auth: bool = True,
        **kwargs
    ) -> Response:
        """
        Execute HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: Endpoint (relative path)
            json: JSON data for request body
            files: Files for multipart/form-data
            data: Form data for application/x-www-form-urlencoded
            params: Query parameters
            requires_auth: Whether authentication is required

        Returns:
            HTTP response

        Raises:
            LightRAGHTTPError: On HTTP errors
        """
        headers = self._get_headers() if requires_auth else {}

        try:
            return await self._client.request(
                method=method,
                url=endpoint,
                headers=headers,
                **kwargs
            )
        except Exception as e:
            raise LightRagHttpError("LightRAG communication error") from e

    def _prepare_file(
        self, file_input: str | Path | bytes | io.BytesIO | Any,
        file_name: str | None
    ) -> tuple[Any, str | None]:
        """
        Prepare file for upload.

        Args:
            file_input: File path, bytes, or file-like object
            file_name: Optional file name

        Returns:
            Tuple (file_object, filename)
        """
        if isinstance(file_input, (str, Path)):
            path = Path(file_input)
            if not path.exists():
                raise LightRagError(f"File not found: {file_input}")
            filename = file_name or path.name
            return open(path, "rb"), filename

        if isinstance(file_input, bytes):
            if file_name is None:
                raise ValueError("File name must be not None if file is bytes")
            return io.BytesIO(file_input), file_name

        # file-like object
        file_name = file_name or getattr(file_input, "name", None)
        if file_name is None:
            raise ValueError("File name must be provided for file-like objects without a name attribute")
        return file_input, file_name

    # ========================================================================
    # Documents methods
    # ========================================================================

    async def scan_documents(self) -> ScanResponse:
        """
        Start scanning for new documents.

        Returns:
            Response with scan status
        """
        response = await self._request("POST", "/documents/scan")
        return ScanResponse(**response.json())

    async def upload_document(
        self,
        file: str | Path | bytes | io.BytesIO | Any,
        file_name: str | None = None,
    ) -> InsertResponse:
        """
        Upload a file to the system.

        Args:
            file: File path, bytes, or file-like object
            file_name: Optional file name

        Returns:
            Upload response
        """
        file_obj, filename = self._prepare_file(file, file_name)
        try:
            files = {"file": (filename, file_obj)}
            response = await self._request("POST", "/documents/upload", files=files)
            return InsertResponse(**response.json())
        finally:
            if hasattr(file_obj, "close") and not isinstance(file_obj, (bytes, io.BytesIO)):
                file_obj.close()

    async def insert_text(self, text: str, file_source: str = "") -> InsertResponse:
        """
        Insert text into the system.

        Args:
            text: Text to insert
            file_source: Text source (optional)

        Returns:
            Insert response
        """
        request = InsertTextRequest(text=text, file_source=file_source)
        response = await self._request("POST", "/documents/text", json=request.model_dump())
        return InsertResponse(**response.json())

    async def insert_texts(
        self, texts: list[str], file_sources: list[str] | None = None
    ) -> InsertResponse:
        """
        Insert multiple texts into the system.

        Args:
            texts: List of texts to insert
            file_sources: List of text sources (optional)

        Returns:
            Insert response
        """
        request = InsertTextsRequest(
            texts=texts, file_sources=file_sources or []
        )
        response = await self._request("POST", "/documents/texts", json=request.model_dump())
        return InsertResponse(**response.json())

    async def get_documents(self) -> DocsStatusesResponse:
        """
        Get statuses of all documents (deprecated).

        Returns:
            Response with document statuses
        """
        response = await self._request("GET", "/documents")
        return DocsStatusesResponse(**response.json())

    async def clear_documents(self) -> ClearDocumentsResponse:
        """
        Clear all documents from the system.

        Returns:
            Clear response
        """
        response = await self._request("DELETE", "/documents")
        return ClearDocumentsResponse(**response.json())

    async def get_pipeline_status(self) -> PipelineStatusResponse:
        """
        Get document processing pipeline status.

        Returns:
            Pipeline status
        """
        response = await self._request("GET", "/documents/pipeline_status")
        return PipelineStatusResponse(**response.json())

    async def delete_document(
        self,
        doc_ids: list[str],
        delete_file: bool = False,
        delete_llm_cache: bool = False,
    ) -> DeleteDocByIdResponse:
        """
        Delete document(s) by ID.

        Args:
            doc_ids: List of document IDs to delete
            delete_file: Delete file from upload directory
            delete_llm_cache: Delete LLM results cache

        Returns:
            Delete response
        """
        request = DeleteDocRequest(
            doc_ids=doc_ids, delete_file=delete_file, delete_llm_cache=delete_llm_cache
        )
        response = await self._request(
            "DELETE", "/documents/delete_document", json=request.model_dump()
        )
        return DeleteDocByIdResponse(**response.json())

    async def clear_cache(self) -> ClearCacheResponse:
        """
        Clear LLM response cache.

        Returns:
            Cache clear response
        """
        request = ClearCacheRequest()
        response = await self._request(
            "POST", "/documents/clear_cache", json=request.model_dump()
        )
        return ClearCacheResponse(**response.json())

    async def delete_entity(self, entity_name: str) -> DeletionResult:
        """
        Delete entity from knowledge graph.

        Args:
            entity_name: Entity name to delete

        Returns:
            Deletion result
        """
        request = DeleteEntityRequest(entity_name=entity_name)
        response = await self._request(
            "DELETE", "/documents/delete_entity", json=request.model_dump()
        )
        return DeletionResult(**response.json())

    async def delete_relation(
        self, source_entity: str, target_entity: str
    ) -> DeletionResult:
        """
        Delete relation between entities.

        Args:
            source_entity: Source entity name
            target_entity: Target entity name

        Returns:
            Deletion result
        """
        request = DeleteRelationRequest(
            source_entity=source_entity, target_entity=target_entity
        )
        response = await self._request(
            "DELETE", "/documents/delete_relation", json=request.model_dump()
        )
        return DeletionResult(**response.json())

    async def get_track_status(self, track_id: str) -> TrackStatusResponse:
        """
        Get document status by track_id.

        Args:
            track_id: Tracking ID

        Returns:
            Tracking status
        """
        response = await self._request("GET", f"/documents/track_status/{track_id}")
        return TrackStatusResponse(**response.json())

    async def get_documents_paginated(
        self,
        status_filter: str | None = None,
        page: int = 1,
        page_size: int = 50,
        sort_field: Literal["created_at", "updated_at", "id", "file_path"] = "updated_at",
        sort_direction: Literal["asc", "desc"] = "desc",
    ) -> PaginatedDocsResponse:
        """
        Get documents with pagination.

        Args:
            status_filter: Status filter (optional)
            page: Page number (starting from 1)
            page_size: Page size (10-200)
            sort_field: Field to sort by
            sort_direction: Sort direction (asc/desc)

        Returns:
            Paginated documents
        """
        request = DocumentsRequest(
            status_filter=status_filter,
            page=page,
            page_size=page_size,
            sort_field=sort_field,
            sort_direction=sort_direction,
        )
        response = await self._request(
            "POST", "/documents/paginated", json=request.model_dump()
        )
        return PaginatedDocsResponse(**response.json())

    async def get_status_counts(self) -> StatusCountsResponse:
        """
        Get document count by status.

        Returns:
            Document count by status
        """
        response = await self._request("GET", "/documents/status_counts")
        return StatusCountsResponse(**response.json())

    async def reprocess_failed(self) -> ReprocessResponse:
        """
        Reprocess failed documents.

        Returns:
            Reprocess response
        """
        response = await self._request("POST", "/documents/reprocess_failed")
        return ReprocessResponse(**response.json())

    async def cancel_pipeline(self) -> CancelPipelineResponse:
        """
        Cancel current processing pipeline.

        Returns:
            Pipeline cancellation response
        """
        response = await self._request("POST", "/documents/cancel_pipeline")
        return CancelPipelineResponse(**response.json())

    # ========================================================================
    # Query methods
    # ========================================================================

    async def query(  # noqa: PLR0913
        self,
        query: str,
        mode: str = "mix",
        include_references: bool = True,
        response_type: str | None = None,
        top_k: int | None = None,
        conversation_history: list[dict[str, str]] | None = None,
        max_total_tokens: int | None = None,
        **kwargs,
    ) -> QueryResponse:
        """
        Execute RAG query.

        Args:
            query: Query text (minimum 3 characters)
            mode: Query mode (local, global, hybrid, naive, mix, bypass)
            include_references: Include references in response
            response_type: Response type (e.g., "Multiple Paragraphs")
            top_k: Number of top elements to extract
            conversation_history: Conversation history
            max_total_tokens: Maximum number of tokens
            **kwargs: Additional QueryRequest parameters

        Returns:
            Query response
        """
        request_data = {
            "query": query,
            "mode": mode,
            "include_references": include_references,
            "response_type": response_type,
            "top_k": top_k,
            "conversation_history": conversation_history,
            "max_total_tokens": max_total_tokens,
            **kwargs,
        }
        # Remove None values
        request_data = {k: v for k, v in request_data.items() if v is not None}

        request = QueryRequest(**request_data)
        response = await self._request("POST", "/query", json=request.model_dump())
        return QueryResponse(**response.json())

    async def query_stream(
        self,
        query: str,
        mode: str = "mix",
        stream: bool = True,
        include_references: bool = True,
        **kwargs,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Execute RAG query with streaming response.

        Args:
            query: Query text (minimum 3 characters)
            mode: Query mode
            stream: Enable streaming
            include_references: Include references in response
            **kwargs: Additional QueryRequest parameters

        Yields:
            Dictionaries with keys: references, response, error
        """
        request_data = {
            "query": query,
            "mode": mode,
            "stream": stream,
            "include_references": include_references,
            **kwargs,
        }
        request_data = {k: v for k, v in request_data.items() if v is not None}

        request = QueryRequest(**request_data)
        url = f"{self.base_url}/query/stream"
        headers = self._get_headers()

        async with self._client.stream(
            "POST", url, json=request.model_dump(), headers=headers
        ) as response:
            if response.is_error:
                raise LightRagHttpError(response.status_code, response.text)

            async for raw_line in response.aiter_lines():
                line = raw_line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    yield data
                except json.JSONDecodeError:
                    # Skip invalid JSON strings
                    continue

    async def query_data(  # noqa: PLR0913
        self,
        query: str,
        mode: str = "mix",
        top_k: int | None = None,
        chunk_top_k: int | None = None,
        max_entity_tokens: int | None = None,
        max_relation_tokens: int | None = None,
        max_total_tokens: int | None = None,
        **kwargs,
    ) -> QueryDataResponse:
        """
        Get structured RAG data without generating response.

        Args:
            query: Query text
            mode: Query mode
            top_k: Number of top elements
            chunk_top_k: Number of top chunks
            max_entity_tokens: Maximum tokens for entities
            max_relation_tokens: Maximum tokens for relations
            max_total_tokens: Maximum total tokens
            **kwargs: Additional parameters

        Returns:
            Structured query data
        """
        request_data = {
            "query": query,
            "mode": mode,
            "top_k": top_k,
            "chunk_top_k": chunk_top_k,
            "max_entity_tokens": max_entity_tokens,
            "max_relation_tokens": max_relation_tokens,
            "max_total_tokens": max_total_tokens,
            **kwargs,
        }
        request_data = {k: v for k, v in request_data.items() if v is not None}

        request = QueryRequest(**request_data)
        response = await self._request("POST", "/query/data", json=request.model_dump())
        return QueryDataResponse(**response.json())

    # ========================================================================
    # Graph methods
    # ========================================================================

    async def get_graph_labels(self) -> list[str]:
        """
        Get all graph labels.

        Returns:
            List of labels
        """
        response = await self._request("GET", "/graph/label/list")
        return response.json()

    async def get_popular_labels(self, limit: int = 300) -> list[str]:
        """
        Get popular labels by node degree.

        Args:
            limit: Maximum number of labels (1-1000)

        Returns:
            List of popular labels
        """
        params = {"limit": limit}
        response = await self._request("GET", "/graph/label/popular", params=params)
        return response.json()

    async def search_labels(self, q: str, limit: int = 50) -> list[str]:
        """
        Search labels with fuzzy matching.

        Args:
            q: Search string
            limit: Maximum number of results (1-100)

        Returns:
            List of found labels
        """
        params = {"q": q, "limit": limit}
        response = await self._request("GET", "/graph/label/search", params=params)
        return response.json()

    async def get_knowledge_graph(
        self, label: str, max_depth: int = 3, max_nodes: int = 1000
    ) -> dict[str, list[str]]:
        """
        Get knowledge subgraph for a label.

        Args:
            label: Initial node label
            max_depth: Maximum subgraph depth
            max_nodes: Maximum number of nodes

        Returns:
            Knowledge graph as a dictionary
        """
        params = {"label": label, "max_depth": max_depth, "max_nodes": max_nodes}
        response = await self._request("GET", "/graphs", params=params)
        return response.json()

    async def check_entity_exists(self, name: str) -> dict[str, bool]:
        """
        Check if entity exists.

        Args:
            name: Entity name

        Returns:
            Dictionary with 'exists' key
        """
        params = {"name": name}
        response = await self._request("GET", "/graph/entity/exists", params=params)
        return response.json()

    async def update_entity(
        self,
        entity_name: str,
        updated_data: dict[str, Any],
        allow_rename: bool = False,
        allow_merge: bool = False,
    ) -> dict[str, Any]:
        """
        Update entity properties.

        Args:
            entity_name: Entity name to update
            updated_data: Dictionary with properties to update
            allow_rename: Allow renaming
            allow_merge: Allow merging on name conflict

        Returns:
            Update result
        """
        request = EntityUpdateRequest(
            entity_name=entity_name,
            updated_data=updated_data,
            allow_rename=allow_rename,
            allow_merge=allow_merge,
        )
        response = await self._request(
            "POST", "/graph/entity/edit", json=request.model_dump()
        )
        return response.json()

    async def update_relation(
        self,
        source_id: str,
        target_id: str,
        updated_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Update relation properties.

        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            updated_data: Dictionary with properties to update

        Returns:
            Update result
        """
        request = RelationUpdateRequest(
            source_id=source_id,
            target_id=target_id,
            updated_data=updated_data,
        )
        response = await self._request(
            "POST", "/graph/relation/edit", json=request.model_dump()
        )
        return response.json()

    async def create_entity(
        self, entity_name: str, entity_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Create a new entity in the knowledge graph.

        Args:
            entity_name: Unique entity name
            entity_data: Entity properties (description, entity_type, etc.)

        Returns:
            Creation result
        """
        request = EntityCreateRequest(entity_name=entity_name, entity_data=entity_data)
        response = await self._request(
            "POST", "/graph/entity/create", json=request.model_dump()
        )
        return response.json()

    async def create_relation(
        self,
        source_entity: str,
        target_entity: str,
        relation_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Create relation between entities.

        Args:
            source_entity: Source entity name
            target_entity: Target entity name
            relation_data: Relation properties (description, keywords, weight, etc.)

        Returns:
            Creation result
        """
        request = RelationCreateRequest(
            source_entity=source_entity,
            target_entity=target_entity,
            relation_data=relation_data,
        )
        response = await self._request(
            "POST", "/graph/relation/create", json=request.model_dump()
        )
        return response.json()

    async def merge_entities(
        self, entities_to_change: list[str], entity_to_change_into: str
    ) -> dict[str, Any]:
        """
        Merge multiple entities into one.

        Args:
            entities_to_change: List of entity names to merge
            entity_to_change_into: Target entity name

        Returns:
            Merge result
        """
        request = EntityMergeRequest(
            entities_to_change=entities_to_change,
            entity_to_change_into=entity_to_change_into,
        )
        response = await self._request(
            "POST", "/graph/entities/merge", json=request.model_dump()
        )
        return response.json()

    # ========================================================================
    # Ollama methods
    # ========================================================================

    async def get_version(self) -> dict[str, Any]:
        """
        Get Ollama version information.

        Returns:
            Version information
        """
        response = await self._request("GET", "/api/version")
        return response.json()

    async def get_tags(self) -> dict[str, Any]:
        """
        Get available models (Ollama compatibility).

        Returns:
            List of available models
        """
        response = await self._request("GET", "/api/tags")
        return response.json()

    async def get_running_models(self) -> dict[str, Any]:
        """
        Get list of running models.

        Returns:
            List of running models
        """
        response = await self._request("GET", "/api/ps")
        return response.json()

    async def generate(self, **kwargs) -> dict[str, Any]:
        """
        Execute generation (Ollama compatibility).

        Args:
            **kwargs: Request parameters

        Returns:
            Generation result
        """
        response = await self._request("POST", "/api/generate", json=kwargs)
        return response.json()

    async def chat(self, **kwargs) -> dict[str, Any]:
        """
        Execute chat request (Ollama compatibility).

        Args:
            **kwargs: Request parameters

        Returns:
            Chat result
        """
        response = await self._request("POST", "/api/chat", json=kwargs)
        return response.json()

    # ========================================================================
    # Auth methods
    # ========================================================================

    async def get_auth_status(self) -> dict[str, Any]:
        """
        Get authentication status.

        Returns:
            Authentication status and guest token (if available)
        """
        response = await self._request("GET", "/auth-status", requires_auth=False)
        return response.json()

    async def login(  # noqa: PLR0913
        self,
        username: str,
        password: str,
        grant_type: str = "password",
        scope: str = "",
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> dict[str, Any]:
        """
        Perform login (OAuth2).

        Args:
            username: Username
            password: Password
            grant_type: Grant type (usually "password")
            scope: Access scope
            client_id: Client ID (optional)
            client_secret: Client secret (optional)

        Returns:
            Access token
        """
        data = {
            "username": username,
            "password": password,
            "grant_type": grant_type,
            "scope": scope,
        }
        if client_id:
            data["client_id"] = client_id
        if client_secret:
            data["client_secret"] = client_secret

        response = await self._request("POST", "/login", data=data, requires_auth=False)
        return response.json()

    async def get_health(self) -> dict[str, Any]:
        """
        Get system status.

        Returns:
            System status
        """
        response = await self._request("GET", "/health")
        return response.json()
