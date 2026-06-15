from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.test_case import TestCaseRead


AssertionType = Literal[
    "status_code",
    "business_code",
    "business_success",
    "json_path_equal",
    "json_path_not_null",
    "json_path_not_empty",
    "json_path_contains",
]
CaseType = Literal["normal", "exception", "boundary", "auth"]


class GeneratedAssertion(BaseModel):
    type: AssertionType
    path: str | None = None
    expected: Any | None = None

    @model_validator(mode="after")
    def validate_assertion_fields(self) -> "GeneratedAssertion":
        if self.type == "status_code" and not isinstance(self.expected, int):
            raise ValueError("status_code assertion requires integer expected")
        if (self.type.startswith("json_path") or self.type.startswith("business_")) and not self.path:
            raise ValueError("json_path assertion requires path")
        if self.type in {"business_code", "business_success", "json_path_equal", "json_path_contains"} and self.expected is None:
            raise ValueError(f"{self.type} assertion requires expected")
        return self


class GeneratedStep(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    request: dict[str, Any]

    @field_validator("request")
    @classmethod
    def validate_request(cls, value: dict[str, Any]) -> dict[str, Any]:
        for key in ("method", "path", "headers", "query", "path_params", "body"):
            if key not in value:
                raise ValueError(f"request requires {key}")
        return value


class GeneratedCase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    case_type: CaseType
    description: str | None = None
    priority: str = Field(default="medium", max_length=32)
    steps: list[GeneratedStep] = Field(..., min_length=1)
    assertions: list[GeneratedAssertion] = Field(..., min_length=1)
    variables: dict[str, Any] | None = None


class GeneratedTestcaseOutput(BaseModel):
    model_name: str = Field(..., min_length=1, max_length=128)
    endpoint: dict[str, Any]
    cases: list[GeneratedCase] = Field(..., min_length=4)

    @field_validator("cases")
    @classmethod
    def validate_case_types(cls, value: list[GeneratedCase]) -> list[GeneratedCase]:
        case_types = {case.case_type for case in value}
        required_types = {"normal", "exception", "boundary", "auth"}
        if case_types != required_types:
            raise ValueError("generated cases must include normal, exception, boundary, and auth")
        return value


class AiGenerationResult(BaseModel):
    endpoint_id: int
    analysis_record_id: int
    case_count: int
    test_cases: list[TestCaseRead]

    model_config = ConfigDict(from_attributes=True)
