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
