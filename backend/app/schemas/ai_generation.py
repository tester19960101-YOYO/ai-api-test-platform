from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.test_case import TestCaseRead


CaseType = Literal["normal", "error", "boundary", "security"]


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
    assertions: list[str] = Field(default_factory=list)
    variables: dict[str, Any] | None = None


class GeneratedTestcaseOutput(BaseModel):
    model_name: str = Field(..., min_length=1, max_length=128)
    provider: str | None = Field(default=None, max_length=32)
    endpoint: dict[str, Any]
    cases: list[GeneratedCase] = Field(..., min_length=10)
    coverage_matrix: dict[str, Any] | None = None
    coverage_summary: dict[str, Any] | None = None

    @field_validator("cases")
    @classmethod
    def validate_case_types(cls, value: list[GeneratedCase]) -> list[GeneratedCase]:
        case_types = {case.case_type for case in value}
        required_types = {"normal", "error", "boundary", "security"}
        if not required_types.issubset(case_types):
            raise ValueError("generated cases must include normal, error, boundary, and security")
        return value


class AiGenerationResult(BaseModel):
    endpoint_id: int
    analysis_record_id: int
    case_count: int
    coverage_matrix: dict[str, Any] | None = None
    coverage_summary: dict[str, Any] | None = None
    test_cases: list[TestCaseRead]

    model_config = ConfigDict(from_attributes=True)
