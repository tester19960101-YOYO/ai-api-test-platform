from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.services.test_case_unified_model import (
    TEST_CASE_PRIORITIES,
    TEST_CASE_STATUSES,
    TEST_CASE_TYPES,
    RISK_LEVELS,
    test_case_to_unified_dict,
)


class TestCaseEndpoint(BaseModel):
    id: int | None = None
    name: str | None = None
    method: str | None = None
    path: str | None = None


class TestCaseAssertion(BaseModel):
    type: str = Field(..., min_length=1, max_length=64)
    path: str | None = None
    operator: str | None = None
    expression: str | None = None
    expected: Any = None
    description: str | None = None
    success_codes: list[Any] | None = None
    success_expression: str | None = None

    model_config = ConfigDict(extra="allow")


class TestCaseRequest(BaseModel):
    method: str | None = None
    path: str | None = None
    headers: dict[str, Any] = Field(default_factory=dict)
    query: dict[str, Any] = Field(default_factory=dict)
    path_params: dict[str, Any] = Field(default_factory=dict)
    body: dict[str, Any] = Field(default_factory=dict)


class TestCaseTimestamps(BaseModel):
    created_at: str | None = None
    updated_at: str | None = None


class TestCaseBase(BaseModel):
    project_id: int = Field(..., gt=0)
    api_endpoint_id: int | None = Field(default=None, gt=0)
    endpoint_name: str | None = Field(default=None, max_length=128)
    endpoint_path: str | None = Field(default=None, max_length=512)
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    type: str = Field(default="functional", max_length=32)
    priority: str = Field(default="P1", max_length=32)
    status: str = Field(default="generated", max_length=32)
    request: TestCaseRequest | dict[str, Any] | None = None
    request_data: dict[str, Any] | None = None
    assertions: list[TestCaseAssertion | dict[str, Any] | str] = Field(default_factory=list)
    dsl_assertions: list[str] = Field(default_factory=list)
    coverage_tag: list[str] = Field(default_factory=list)
    risk_level: str = Field(default="medium", max_length=32)
    data_dependency: dict[str, Any] = Field(default_factory=dict)
    ai_metadata: dict[str, Any] = Field(default_factory=dict)

    # Legacy input fields accepted only for migration compatibility.
    steps: list[Any] | None = None
    variables: dict[str, Any] | None = None

class TestCaseCreate(TestCaseBase):
    pass


class TestCaseUpdate(BaseModel):
    api_endpoint_id: int | None = Field(default=None, gt=0)
    endpoint_name: str | None = Field(default=None, max_length=128)
    endpoint_path: str | None = Field(default=None, max_length=512)
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    type: str | None = Field(default=None, max_length=32)
    priority: str | None = Field(default=None, max_length=32)
    status: str | None = Field(default=None, max_length=32)
    request: TestCaseRequest | dict[str, Any] | None = None
    request_data: dict[str, Any] | None = None
    assertions: list[TestCaseAssertion | dict[str, Any] | str] | None = None
    dsl_assertions: list[str] | None = None
    coverage_tag: list[str] | None = None
    risk_level: str | None = Field(default=None, max_length=32)
    data_dependency: dict[str, Any] | None = None
    ai_metadata: dict[str, Any] | None = None

    # Legacy input fields accepted only for migration compatibility.
    steps: list[Any] | None = None
    variables: dict[str, Any] | None = None


class TestCaseRead(BaseModel):
    id: int
    project_id: int
    api_endpoint_id: int | None = None
    endpoint_name: str | None = None
    endpoint_path: str | None = None
    name: str
    description: str | None = None
    endpoint: TestCaseEndpoint | None = None
    type: str
    priority: str
    status: str
    request: TestCaseRequest | dict[str, Any] | None = None
    request_data: dict[str, Any] | None = None
    assertions: list[TestCaseAssertion | dict[str, Any] | str] = Field(default_factory=list)
    dsl_assertions: list[str] = Field(default_factory=list)
    coverage_tag: list[str] = Field(default_factory=list)
    risk_level: str
    data_dependency: dict[str, Any] = Field(default_factory=dict)
    ai_metadata: dict[str, Any] = Field(default_factory=dict)
    timestamps: TestCaseTimestamps
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def from_orm_test_case(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return value
        if hasattr(value, "__tablename__") and getattr(value, "__tablename__", "") == "test_case":
            return test_case_to_unified_dict(value)
        return value
