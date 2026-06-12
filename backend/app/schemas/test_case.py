from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TestCaseBase(BaseModel):
    project_id: int = Field(..., gt=0)
    api_endpoint_id: int | None = Field(default=None, gt=0)
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    priority: str = Field(default="medium", max_length=32)
    status: str = Field(default="draft", max_length=32)
    steps: list[Any] | None = None
    assertions: list[Any] | None = None
    variables: dict[str, Any] | None = None


class TestCaseCreate(TestCaseBase):
    pass


class TestCaseUpdate(BaseModel):
    api_endpoint_id: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    priority: str | None = Field(default=None, max_length=32)
    status: str | None = Field(default=None, max_length=32)
    steps: list[Any] | None = None
    assertions: list[Any] | None = None
    variables: dict[str, Any] | None = None


class TestCaseRead(TestCaseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
