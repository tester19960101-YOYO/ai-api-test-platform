from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EnvironmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    base_url: str = Field(..., min_length=1, max_length=512)
    variables: dict[str, Any] | None = None
    headers: dict[str, Any] | None = None
    is_default: bool = False
    status: str = Field(default="active", max_length=32)


class EnvironmentCreate(EnvironmentBase):
    pass


class EnvironmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    base_url: str | None = Field(default=None, min_length=1, max_length=512)
    variables: dict[str, Any] | None = None
    headers: dict[str, Any] | None = None
    is_default: bool | None = None
    status: str | None = Field(default=None, max_length=32)


class EnvironmentRead(EnvironmentBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
