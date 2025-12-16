import asyncio
import io
from collections.abc import Coroutine, Generator
from pathlib import Path
from typing import Any, Literal, TypeVar

from httpx import AsyncClient

from lightrag.api._schemas import (
    CancelPipelineResponse,
    ClearCacheResponse,
    ClearDocumentsResponse,
    DeleteDocByIdResponse,
    DeletionResult,
    DocsStatusesResponse,
    InsertResponse,
    PaginatedDocsResponse,
    PipelineStatusResponse,
    QueryDataResponse,
    QueryResponse,
    ReprocessResponse,
    ScanResponse,
    StatusCountsResponse,
    TrackStatusResponse,
)

from ._async_client import AsyncLightRagClient

_T = TypeVar("_T")


class SyncLightRagClient:
    """
    Synchronous HTTP client for LightRAG API.

    Provides convenient methods for working with all API endpoints.
    """

    def __init__(  # noqa: PLR0913
        self,
        base_url: str,
        api_key: str | None = None,
        oauth_token: str | None = None,
        client: AsyncClient | None = None,
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
        self._async_client = AsyncLightRagClient(
            base_url=base_url,
            api_key=api_key,
            oauth_token=oauth_token,
            async_client=client,
            client_timeout=client_timeout,
            verify_ssl=verify_ssl,
        )

    def _is_no_running_loop(self) -> bool:
        """
        Check if event loop is running.

        Returns:
            True if loop is running, False otherwise
        """
        try:
            asyncio.get_running_loop()
            return False
        except RuntimeError:
            return True

    def _run_async(self, coro: Coroutine[Any, Any, _T]) -> _T:
        """Execute async function synchronously."""
        if self._is_no_running_loop():
            # No running loop - create a new one via asyncio.run()
            return asyncio.run(coro)

        # Loop is already running - create a task and wait via Future
        from concurrent.futures import Future  # noqa: PLC0415

        future = Future()

        def set_result(task):
            try:
                future.set_result(task.result())
            except Exception as e:
                future.set_exception(e)

        loop = asyncio.get_running_loop()
        task = loop.create_task(coro)
        task.add_done_callback(set_result)

        # Synchronously wait for result (blocks current thread)
        return future.result()

    def close(self):
        """Close the client and release resources."""
        self._run_async(self._async_client.close())

    # ========================================================================
    # Documents methods
    # ========================================================================

    def scan_documents(self) -> ScanResponse:
        """
        Start scanning for new documents.

        Returns:
            Response with scanning status
        """
        return self._run_async(self._async_client.scan_documents())


    def upload_document(
        self, file: str | Path | bytes | io.BytesIO | Any,
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
        return self._run_async(self._async_client.upload_document(file, file_name))

    def insert_text(self, text: str, file_source: str = "") -> InsertResponse:
        """
        Insert text into the system.

        Args:
            text: Text to insert
            file_source: Text source (optional)

        Returns:
            Insert response
        """
        return self._run_async(self._async_client.insert_text(text, file_source))

    def insert_texts(
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
        return self._run_async(self._async_client.insert_texts(texts, file_sources))

    def get_documents(self) -> DocsStatusesResponse:
        """
        Get statuses of all documents (deprecated).

        Returns:
            Response with document statuses
        """
        return self._run_async(self._async_client.get_documents())

    def clear_documents(self) -> ClearDocumentsResponse:
        """
        Clear all documents from the system.

        Returns:
            Clear response
        """
        return self._run_async(self._async_client.clear_documents())

    def get_pipeline_status(self) -> PipelineStatusResponse:
        """
        Get the document processing pipeline status.

        Returns:
            Pipeline status
        """
        return self._run_async(self._async_client.get_pipeline_status())

    def delete_document(
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
            Deletion response
        """
        return self._run_async(
            self._async_client.delete_document(doc_ids, delete_file, delete_llm_cache)
        )

    def clear_cache(self) -> ClearCacheResponse:
        """
        Clear LLM response cache.

        Returns:
            Cache clear response
        """
        return self._run_async(self._async_client.clear_cache())

    def delete_entity(self, entity_name: str) -> DeletionResult:
        """
        Delete an entity from the knowledge graph.

        Args:
            entity_name: Name of the entity to delete

        Returns:
            Deletion result
        """
        return self._run_async(self._async_client.delete_entity(entity_name))

    def delete_relation(
        self, source_entity: str, target_entity: str
    ) -> DeletionResult:
        """
        Delete a relation between entities.

        Args:
            source_entity: Name of the source entity
            target_entity: Name of the target entity

        Returns:
            Deletion result
        """
        return self._run_async(
            self._async_client.delete_relation(source_entity, target_entity)
        )

    def get_track_status(self, track_id: str) -> TrackStatusResponse:
        """
        Get document status by track_id.

        Args:
            track_id: Tracking ID

        Returns:
            Tracking status
        """
        return self._run_async(self._async_client.get_track_status(track_id))

    def get_documents_paginated(
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
        return self._run_async(
            self._async_client.get_documents_paginated(
                status_filter, page, page_size, sort_field, sort_direction
            )
        )

    def get_status_counts(self) -> StatusCountsResponse:
        """
        Get document counts by status.

        Returns:
            Document counts by status
        """
        return self._run_async(self._async_client.get_status_counts())

    def reprocess_failed(self) -> ReprocessResponse:
        """
        Reprocess failed documents.

        Returns:
            Reprocess response
        """
        return self._run_async(self._async_client.reprocess_failed())

    def cancel_pipeline(self) -> CancelPipelineResponse:
        """
        Cancel the current processing pipeline.

        Returns:
            Pipeline cancellation response
        """
        return self._run_async(self._async_client.cancel_pipeline())

    # ========================================================================
    # Query methods
    # ========================================================================

    def query(  # noqa: PLR0913
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
        Execute a RAG query.

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
        return self._run_async(
            self._async_client.query(
                query,
                mode,
                include_references,
                response_type,
                top_k,
                conversation_history,
                max_total_tokens,
                **kwargs,
            )
        )

    def query_stream(
        self,
        query: str,
        mode: str = "mix",
        stream: bool = True,
        include_references: bool = True,
        **kwargs,
    ) -> Generator[dict[str, Any], None, None]:
        """
        Execute a RAG query with streaming response.

        Args:
            query: Query text (minimum 3 characters)
            mode: Query mode
            stream: Enable streaming
            include_references: Include references in response
            **kwargs: Additional QueryRequest parameters

        Yields:
            Dictionaries with keys: references, response, error
        """
        async_gen = self._async_client.query_stream(
            query, mode, stream, include_references, **kwargs
        )

        async def consume():
            results = []
            async for item in async_gen:
                results.append(item)  # noqa: PERF401
            return results

        results = self._run_async(consume())
        yield from results

    def query_data(  # noqa: PLR0913
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
        Get structured RAG data without generating a response.

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
        return self._run_async(
            self._async_client.query_data(
                query,
                mode,
                top_k,
                chunk_top_k,
                max_entity_tokens,
                max_relation_tokens,
                max_total_tokens,
                **kwargs,
            )
        )

    # ========================================================================
    # Graph methods
    # ========================================================================

    def get_graph_labels(self) -> list[str]:
        """
        Get all graph labels.

        Returns:
            List of labels
        """
        return self._run_async(self._async_client.get_graph_labels())

    def get_popular_labels(self, limit: int = 300) -> list[str]:
        """
        Get popular labels by node degree.

        Args:
            limit: Maximum number of labels (1-1000)

        Returns:
            List of popular labels
        """
        return self._run_async(self._async_client.get_popular_labels(limit))

    def search_labels(self, q: str, limit: int = 50) -> list[str]:
        """
        Search labels with fuzzy matching.

        Args:
            q: Search string
            limit: Maximum number of results (1-100)

        Returns:
            List of found labels
        """
        return self._run_async(self._async_client.search_labels(q, limit))

    def get_knowledge_graph(
        self, label: str, max_depth: int = 3, max_nodes: int = 1000
    ) -> dict[str, list[str]]:
        """
        Get knowledge subgraph for a label.

        Args:
            label: Starting node label
            max_depth: Maximum subgraph depth
            max_nodes: Maximum number of nodes

        Returns:
            Knowledge graph as a dictionary
        """
        return self._run_async(
            self._async_client.get_knowledge_graph(label, max_depth, max_nodes)
        )

    def check_entity_exists(self, name: str) -> dict[str, bool]:
        """
        Check if an entity exists.

        Args:
            name: Entity name

        Returns:
            Dictionary with 'exists' key
        """
        return self._run_async(self._async_client.check_entity_exists(name))

    def update_entity(
        self,
        entity_name: str,
        updated_data: dict[str, Any],
        allow_rename: bool = False,
        allow_merge: bool = False,
    ) -> dict[str, Any]:
        """
        Update entity properties.

        Args:
            entity_name: Name of the entity to update
            updated_data: Dictionary with properties to update
            allow_rename: Allow renaming
            allow_merge: Allow merging on name conflict

        Returns:
            Update result
        """
        return self._run_async(
            self._async_client.update_entity(
                entity_name, updated_data, allow_rename, allow_merge
            )
        )

    def update_relation(
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
        return self._run_async(
            self._async_client.update_relation(source_id, target_id, updated_data)
        )

    def create_entity(
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
        return self._run_async(
            self._async_client.create_entity(entity_name, entity_data)
        )

    def create_relation(
        self,
        source_entity: str,
        target_entity: str,
        relation_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Create a relation between entities.

        Args:
            source_entity: Source entity name
            target_entity: Target entity name
            relation_data: Relation properties (description, keywords, weight, etc.)

        Returns:
            Creation result
        """
        return self._run_async(
            self._async_client.create_relation(
                source_entity, target_entity, relation_data
            )
        )

    def merge_entities(
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
        return self._run_async(
            self._async_client.merge_entities(entities_to_change, entity_to_change_into)
        )

    # ========================================================================
    # Ollama methods
    # ========================================================================

    def get_version(self) -> dict[str, Any]:
        """
        Get Ollama version information.

        Returns:
            Version information
        """
        return self._run_async(self._async_client.get_version())

    def get_tags(self) -> dict[str, Any]:
        """
        Get available models (Ollama compatibility).

        Returns:
            List of available models
        """
        return self._run_async(self._async_client.get_tags())

    def get_running_models(self) -> dict[str, Any]:
        """
        Get list of running models.

        Returns:
            List of running models
        """
        return self._run_async(self._async_client.get_running_models())

    def generate(self, **kwargs) -> dict[str, Any]:
        """
        Execute generation (Ollama compatibility).

        Args:
            **kwargs: Request parameters

        Returns:
            Generation result
        """
        return self._run_async(self._async_client.generate(**kwargs))

    def chat(self, **kwargs) -> dict[str, Any]:
        """
        Execute a chat request (Ollama compatibility).

        Args:
            **kwargs: Request parameters

        Returns:
            Chat result
        """
        return self._run_async(self._async_client.chat(**kwargs))

    # ========================================================================
    # Auth methods
    # ========================================================================

    def get_auth_status(self) -> dict[str, Any]:
        """
        Get authentication status.

        Returns:
            Authentication status and guest token (if available)
        """
        return self._run_async(self._async_client.get_auth_status())

    def login(  # noqa: PLR0913
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
        return self._run_async(
            self._async_client.login(
                username, password, grant_type, scope, client_id, client_secret
            )
        )

    def get_health(self) -> dict[str, Any]:
        """
        Get system status.

        Returns:
            System status
        """
        return self._run_async(self._async_client.get_health())
