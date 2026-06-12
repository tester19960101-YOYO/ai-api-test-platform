from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ApiEndpointUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    method: str | None = Field(default=None, min_length=1, max_length=16)
    path: str | None = Field(default=None, min_length=1, max_length=512)
    description: str | None = None
    group_name: str | None = Field(default=None, max_length=128)
    headers: dict[str, Any] | None = None
    request_params: dict[str, Any] | None = None
    request_body_schema: dict[str, Any] | None = None
    response_schema: dict[str, Any] | None = None
    example_request: dict[str, Any] | None = None
    example_response: dict[str, Any] | None = None
    auth_required: bool | None = None
    tags: list[Any] | None = None
    status: str | None = Field(default=None, max_length=32)

    @field_validator("method")
    @classmethod
    def normalize_method(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.upper()


class ApiEndpointRead(BaseModel):
    id: int
    project_id: int
    api_document_id: int | None
    name: str
    group_name: str | None
    method: str
    path: str
    description: str | None
    headers: dict[str, Any] | None
    request_params: dict[str, Any] | None
    request_body_schema: dict[str, Any] | None
    response_schema: dict[str, Any] | None
    example_request: dict[str, Any] | None
    example_response: dict[str, Any] | None
    auth_required: bool
    tags: list[Any] | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
