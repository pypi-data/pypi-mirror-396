from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# Common models
class PaginationInfo(BaseModel):
    """Информация о пагинации."""

    page: int
    page_size: int
    total_count: int
    total_pages: int
    has_next: bool
    has_prev: bool


class ValidationError(BaseModel):
    """Ошибка валидации."""

    loc: list[str | int]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    """HTTP ошибка валидации."""

    detail: list[ValidationError]


# Query models
class ReferenceItem(BaseModel):
    """Элемент ссылки в ответе запроса."""

    reference_id: str
    file_path: str
    content: list[str] | None = None


class QueryRequest(BaseModel):
    """Запрос для RAG запроса."""

    query: str = Field(..., min_length=3)
    mode: Literal["local", "global", "hybrid", "naive", "mix", "bypass"] = "mix"
    only_need_context: bool | None = None
    only_need_prompt: bool | None = None
    response_type: str | None = Field(None, min_length=1)
    top_k: int | None = Field(None, ge=1)
    chunk_top_k: int | None = Field(None, ge=1)
    max_entity_tokens: int | None = Field(None, ge=1)
    max_relation_tokens: int | None = Field(None, ge=1)
    max_total_tokens: int | None = Field(None, ge=1)
    hl_keywords: list[str] = Field(default_factory=list)
    ll_keywords: list[str] = Field(default_factory=list)
    conversation_history: list[dict[str, Any]] | None = None
    user_prompt: str | None = None
    enable_rerank: bool | None = None
    include_references: bool | None = True
    include_chunk_content: bool | None = False
    stream: bool | None = True


class QueryResponse(BaseModel):
    """Ответ на RAG запрос."""

    response: str
    references: list[ReferenceItem] | None = None


class QueryDataResponse(BaseModel):
    """Ответ на запрос данных RAG."""

    status: str
    message: str
    data: dict[str, Any]
    metadata: dict[str, Any]


# Documents models
class DocStatus(str, Enum):
    """Статус документа."""

    PENDING = "pending"
    PROCESSING = "processing"
    PREPROCESSED = "preprocessed"
    PROCESSED = "processed"
    FAILED = "failed"


class InsertTextRequest(BaseModel):
    """Запрос на вставку текста."""

    text: str = Field(..., min_length=1)
    file_source: str = Field(default="")


class InsertTextsRequest(BaseModel):
    """Запрос на вставку нескольких текстов."""

    texts: list[str] = Field(min_length=1)
    file_sources: list[str] = Field(default_factory=list)


class InsertResponse(BaseModel):
    """Ответ на операцию вставки."""

    status: str
    message: str
    track_id: str


class DocStatusResponse(BaseModel):
    """Статус документа."""

    id: str
    content_summary: str
    content_length: int
    status: str
    created_at: str
    updated_at: str
    file_path: str
    track_id: str | None = None
    chunks_count: int | None = None
    error_msg: str | None = None
    metadata: dict[str, Any] | None = None


class DocumentsRequest(BaseModel):
    """Запрос на получение документов с пагинацией."""

    status_filter: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=10, le=200)
    sort_field: Literal["created_at", "updated_at", "id", "file_path"] = "updated_at"
    sort_direction: Literal["asc", "desc"] = "desc"


class PaginatedDocsResponse(BaseModel):
    """Ответ с пагинированными документами."""

    documents: list[DocStatusResponse]
    pagination: PaginationInfo
    status_counts: dict[str, int]


class DocsStatusesResponse(BaseModel):
    """Ответ со статусами документов."""

    statuses: dict[str, list[DocStatusResponse]]


class ScanResponse(BaseModel):
    """Ответ на запрос сканирования."""

    status: str
    message: str | None = None
    track_id: str


class ClearDocumentsResponse(BaseModel):
    """Ответ на очистку документов."""

    status: str
    message: str


class DeleteDocRequest(BaseModel):
    """Запрос на удаление документа."""

    doc_ids: list[str]
    delete_file: bool = False
    delete_llm_cache: bool = False


class DeleteDocByIdResponse(BaseModel):
    """Ответ на удаление документа."""

    status: str
    message: str
    doc_id: str


class ClearCacheRequest(BaseModel):
    """Запрос на очистку кэша."""


class ClearCacheResponse(BaseModel):
    """Ответ на очистку кэша."""

    status: str
    message: str


class PipelineStatusResponse(BaseModel):
    """Статус пайплайна обработки документов."""

    autoscanned: bool = False
    busy: bool = False
    job_name: str = "Default Job"
    job_start: str | None = None
    docs: int = 0
    batchs: int = 0
    cur_batch: int = 0
    request_pending: bool = False
    latest_message: str = ""
    history_messages: list[str] | None = None
    update_status: dict[str, Any] | None = None


class TrackStatusResponse(BaseModel):
    """Статус отслеживания документов."""

    track_id: str
    documents: list[DocStatusResponse]
    total_count: int
    status_summary: dict[str, int]


class StatusCountsResponse(BaseModel):
    """Количество документов по статусам."""

    status_counts: dict[str, int]


class ReprocessResponse(BaseModel):
    """Ответ на запрос повторной обработки."""

    status: str
    message: str
    track_id: str


class CancelPipelineResponse(BaseModel):
    """Ответ на запрос отмены пайплайна."""

    status: str
    message: str


class DeleteEntityRequest(BaseModel):
    """Запрос на удаление сущности."""

    entity_name: str


class DeleteRelationRequest(BaseModel):
    """Запрос на удаление связи."""

    source_entity: str
    target_entity: str


class DeletionResult(BaseModel):
    """Результат удаления."""

    status: str
    doc_id: str
    message: str
    status_code: int = 200
    file_path: str | None = None


# Graph models
class EntityCreateRequest(BaseModel):
    """Запрос на создание сущности."""

    entity_name: str = Field(..., min_length=1)
    entity_data: dict[str, Any]


class EntityUpdateRequest(BaseModel):
    """Запрос на обновление сущности."""

    entity_name: str
    updated_data: dict[str, Any]
    allow_rename: bool = False
    allow_merge: bool = False


class EntityMergeRequest(BaseModel):
    """Запрос на объединение сущностей."""

    entities_to_change: list[str] = Field(..., min_length=1)
    entity_to_change_into: str = Field(..., min_length=1)


class RelationCreateRequest(BaseModel):
    """Запрос на создание связи."""

    source_entity: str = Field(..., min_length=1)
    target_entity: str = Field(..., min_length=1)
    relation_data: dict[str, Any]


class RelationUpdateRequest(BaseModel):
    """Запрос на обновление связи."""

    source_id: str
    target_id: str
    updated_data: dict[str, Any]


# Auth models
class LoginRequest(BaseModel):
    """Запрос на логин (для form-urlencoded)."""

    username: str
    password: str
    grant_type: str | None = "password"
    scope: str = ""
    client_id: str | None = None
    client_secret: str | None = None

