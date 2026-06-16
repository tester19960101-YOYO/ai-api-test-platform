from typing import Any

from app.core.assertion_dsl import parse_assertion_dsl
from app.models.api_endpoint import ApiEndpoint


VALID_CASE_TYPES = {"normal", "error", "boundary"}


class TestcaseStandardizationError(ValueError):
    pass


def standardize_ai_testcases(raw_output: dict[str, Any], endpoint: ApiEndpoint) -> dict[str, Any]:
    """Normalize model output into the platform's executable test_case structure."""

    raw_cases = raw_output.get("test_cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise TestcaseStandardizationError("AI output requires non-empty test_cases")

    cases = [_standardize_case(item, endpoint, index) for index, item in enumerate(raw_cases, start=1)]
    case_types = {case["case_type"] for case in cases}
    missing = VALID_CASE_TYPES - case_types
    if missing:
        raise TestcaseStandardizationError(f"AI output missing case types: {sorted(missing)}")
    return {
        "model_name": raw_output.get("model_name") or "real-ai-testcase-generator",
        "endpoint": {
            "id": endpoint.id,
            "name": endpoint.name,
            "method": endpoint.method,
            "path": endpoint.path,
            "auth_required": endpoint.auth_required,
        },
        "cases": cases,
    }


def _standardize_case(raw_case: Any, endpoint: ApiEndpoint, index: int) -> dict[str, Any]:
    if not isinstance(raw_case, dict):
        raise TestcaseStandardizationError(f"test case #{index} must be an object")

    case_type = str(raw_case.get("type") or raw_case.get("case_type") or "").strip().lower()
    if case_type not in VALID_CASE_TYPES:
        raise TestcaseStandardizationError(f"test case #{index} has invalid type: {case_type}")

    request = _normalize_request(raw_case.get("request"), endpoint, index)
    assertions = _normalize_assertions(raw_case.get("assertions"), index)
    name = str(raw_case.get("name") or f"{endpoint.name}-{case_type}").strip()
    description = raw_case.get("description") or f"AI generated {case_type} testcase"

    return {
        "name": name[:128],
        "case_type": case_type,
        "description": str(description),
        "priority": str(raw_case.get("priority") or "medium")[:32],
        "steps": [{"name": f"{request['method']} {request['path']}", "request": request}],
        "assertions": assertions,
        "variables": {
            "generated_by": "ai_openai",
            "source": "ai_openai",
            "case_type": case_type,
            "source_endpoint_id": endpoint.id,
            "standardized": True,
        },
    }


def _normalize_request(raw_request: Any, endpoint: ApiEndpoint, index: int) -> dict[str, Any]:
    if not isinstance(raw_request, dict):
        raise TestcaseStandardizationError(f"test case #{index} request must be an object")
    missing = [key for key in ("headers", "query", "path", "body") if key not in raw_request]
    if missing:
        raise TestcaseStandardizationError(f"test case #{index} request missing fields: {missing}")
    path_params = raw_request.get("path_params") if "path_params" in raw_request else raw_request.get("path")
    return {
        "method": str(raw_request.get("method") or endpoint.method or "GET").upper(),
        "path": str(endpoint.path or raw_request.get("url_path") or "/"),
        "headers": _dict_or_empty(raw_request.get("headers"), index, "headers"),
        "query": _dict_or_empty(raw_request.get("query"), index, "query"),
        "path_params": _dict_or_empty(path_params, index, "path"),
        "body": _dict_or_empty(raw_request.get("body"), index, "body"),
    }


def _normalize_assertions(raw_assertions: Any, index: int) -> list[str]:
    if not isinstance(raw_assertions, list) or not raw_assertions:
        raise TestcaseStandardizationError(f"test case #{index} assertions must be a non-empty DSL string array")
    assertions: list[str] = []
    for item in raw_assertions:
        if not isinstance(item, str):
            raise TestcaseStandardizationError(f"test case #{index} assertions must only contain DSL strings")
        assertion = " ".join(item.strip().split())
        if not assertion:
            raise TestcaseStandardizationError(f"test case #{index} assertion cannot be empty")
        if assertion.lower().replace(" ", "") in {"business_code==1", "$.business_code==1"}:
            raise TestcaseStandardizationError("AI assertions must not hard-code business_code == 1")
        assertions.append(assertion)
    for assertion in assertions:
        parse_assertion_dsl(assertion, source="ai", enabled=False)
    return assertions


def _dict_or_empty(value: Any, index: int, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TestcaseStandardizationError(f"test case #{index} request.{field_name} must be an object")
    return value
