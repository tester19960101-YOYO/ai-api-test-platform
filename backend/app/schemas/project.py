from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    owner_name: str | None = Field(default=None, max_length=128)
    status: str = Field(default="active", max_length=32)
    config: dict[str, Any] | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    owner_name: str | None = Field(default=None, max_length=128)
    status: str | None = Field(default=None, max_length=32)
    config: dict[str, Any] | None = None


class ProjectRead(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
