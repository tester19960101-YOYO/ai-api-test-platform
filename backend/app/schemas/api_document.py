from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.api_endpoint import ApiEndpointRead


class OpenApiImportRequest(BaseModel):
    name: str = Field(default="OpenAPI Document", min_length=1, max_length=128)
    content: dict[str, Any] | None = None
    url: str | None = Field(default=None, max_length=1024)

    @model_validator(mode="after")
    def validate_source(self) -> "OpenApiImportRequest":
        if self.content is None and not self.url:
            raise ValueError("content or url is required")
        return self


class CurlImportRequest(BaseModel):
    name: str = Field(default="curl Document", min_length=1, max_length=128)
    curl_text: str = Field(..., min_length=1)


class ApiDocumentRead(BaseModel):
    id: int
    project_id: int
    name: str
    source_type: str
    file_path: str | None
    raw_content: str | None
    parsed_data: dict[str, Any] | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApiDocumentImportResult(BaseModel):
    document: ApiDocumentRead
    endpoints: list[ApiEndpointRead]
    endpoint_count: int


class EndpointPreviewItem(BaseModel):
    endpoint_key: str
    name: str = Field(..., min_length=1, max_length=128)
    group_name: str | None = Field(default=None, max_length=128)
    summary: str | None = None
    operation_id: str | None = None
    method: str = Field(..., min_length=1, max_length=16)
    path: str = Field(..., min_length=1, max_length=512)
    description: str | None = None
    headers: dict[str, Any] | None = None
    request_params: dict[str, Any] | None = None
    request_body_schema: dict[str, Any] | None = None
    response_schema: dict[str, Any] | None = None
    example_request: dict[str, Any] | None = None
    example_response: Any | None = None
    auth_required: bool = False
    tags: list[Any] | None = None
    status: str = Field(default="active", max_length=32)
    source: str = Field(default="parsed", max_length=32)


class DocumentPreviewRequest(BaseModel):
    name: str = Field(default="API Document", min_length=1, max_length=128)
    input_type: str = Field(default="auto", max_length=32)
    input_content: str = Field(..., min_length=1)
    cookie: str | None = Field(default=None, max_length=4096)
    api_path_filter: str | None = Field(default=None, max_length=512)
    method_filter: str | None = Field(default=None, max_length=16)
    keyword_filter: str | None = Field(default=None, max_length=128)
    group_filter: str | None = Field(default=None, max_length=128)
    need_ai_parse: bool = True


class DocumentPreviewResponse(BaseModel):
    detected_type: str
    resolved_spec_url: str | None = None
    hash_hint: str | None = None
    total_endpoint_count: int
    matched_endpoint_count: int
    endpoints: list[EndpointPreviewItem]
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class DocumentImportUrlRequest(DocumentPreviewRequest):
    save_mode: str = Field(default="save_all", pattern="^(save_selected|save_all)$")
    selected_endpoint_keys: list[str] = Field(default_factory=list)
    endpoints: list[EndpointPreviewItem] | None = None


class DocumentImportUrlResponse(BaseModel):
    document: ApiDocumentRead
    endpoints: list[ApiEndpointRead]
    endpoint_count: int
    detected_type: str
    resolved_spec_url: str | None = None
    hash_hint: str | None = None
    total_endpoint_count: int
    matched_endpoint_count: int
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
