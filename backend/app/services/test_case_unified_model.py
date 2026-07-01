from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core.assertion_dsl import assertion_to_dsl, parse_assertion_dsl


TEST_CASE_TYPES = {"functional", "validation", "boundary", "negative", "security", "business", "dependency"}
TEST_CASE_PRIORITIES = {"P0", "P1", "P2"}
TEST_CASE_STATUSES = {"generated", "edited", "disabled", "passed", "failed"}
RISK_LEVELS = {"low", "medium", "high"}

LEGACY_TYPE_MAP = {
    "normal": "functional",
    "error": "negative",
    "exception": "negative",
    "boundary": "boundary",
    "auth": "security",
    "security": "security",
}
LEGACY_STATUS_MAP = {
    "active": "edited",
    "draft": "edited",
    "inactive": "disabled",
}
LEGACY_PRIORITY_MAP = {
    "high": "P0",
    "medium": "P1",
    "low": "P2",
}
PRIORITY_TO_RISK = {"P0": "high", "P1": "medium", "P2": "low"}
RISK_TO_PRIORITY = {"high": "P0", "medium": "P1", "low": "P2"}


class TestCaseUnifiedModelError(ValueError):
    pass


def normalize_test_case_data(data: dict[str, Any], endpoint: Any | None = None) -> dict[str, Any]:
    normalized = dict(data)
    endpoint_id = normalized.get("api_endpoint_id") or getattr(endpoint, "id", None)
    endpoint_name = normalized.get("endpoint_name") or getattr(endpoint, "name", None)
    endpoint_path = normalized.get("endpoint_path") or getattr(endpoint, "path", None)

    normalized["api_endpoint_id"] = endpoint_id
    normalized["endpoint_name"] = endpoint_name
    normalized["endpoint_path"] = endpoint_path
    normalized["type"] = normalize_type(normalized.get("type") or _legacy_coverage_dimension(normalized))
    normalized["priority"] = normalize_priority(normalized.get("priority"), normalized.get("risk_level"))
    normalized["status"] = normalize_status(normalized.get("status"))
    normalized["risk_level"] = normalize_risk_level(normalized.get("risk_level"), normalized["priority"])
    normalized["request_data"] = normalize_request_data(normalized.get("request") or normalized.get("request_data"), normalized, endpoint)
    normalized["dsl_assertions"] = normalize_dsl_assertions(normalized.get("dsl_assertions") or normalized.get("assertions"))
    normalized["assertions"] = normalize_structured_assertions(
        normalized.get("assertions"),
        normalized["dsl_assertions"],
    )
    normalized["coverage_tag"] = normalize_coverage_tag(normalized.get("coverage_tag"), normalized["type"])
    normalized["data_dependency"] = _dict_or_empty(normalized.get("data_dependency"))
    normalized["ai_metadata"] = _dict_or_empty(normalized.get("ai_metadata"))
    normalized["variables"] = normalize_legacy_variables(normalized)
    normalized["steps"] = normalize_legacy_steps(normalized)

    normalized.pop("request", None)
    return normalized


def test_case_to_unified_dict(test_case: Any) -> dict[str, Any]:
    endpoint = getattr(test_case, "api_endpoint", None)
    legacy_data = _orm_to_dict(test_case)
    legacy_variables = _dict_or_empty(legacy_data.get("variables"))
    legacy_dimension = legacy_variables.get("coverage_dimension") or legacy_variables.get("case_type")
    legacy_dsl_assertions = legacy_variables.get("ai_assertion_dsl")
    legacy_priority = legacy_variables.get("risk_level")
    endpoint_data = {
        "id": getattr(test_case, "api_endpoint_id", None),
        "name": getattr(test_case, "endpoint_name", None) or getattr(endpoint, "name", None),
        "method": getattr(endpoint, "method", None),
        "path": getattr(test_case, "endpoint_path", None) or getattr(endpoint, "path", None),
    }
    request_data = normalize_request_data(getattr(test_case, "request_data", None), legacy_data, endpoint)
    dsl_assertions = normalize_dsl_assertions(
        getattr(test_case, "dsl_assertions", None) or getattr(test_case, "assertions", None)
    )
    if not dsl_assertions:
        dsl_assertions = normalize_dsl_assertions(legacy_dsl_assertions)
    assertions = normalize_structured_assertions(getattr(test_case, "assertions", None), dsl_assertions)
    priority_source = getattr(test_case, "priority", None)
    if legacy_priority and str(priority_source or "").upper() in {"", "P1", "MEDIUM"}:
        priority_source = legacy_priority
    priority = normalize_priority(priority_source, getattr(test_case, "risk_level", None))
    status = normalize_status(getattr(test_case, "status", None))
    type_source = getattr(test_case, "type", None)
    if legacy_dimension and str(type_source or "").strip().lower() in {"", "functional"}:
        type_source = legacy_dimension
    case_type = normalize_type(type_source or _legacy_coverage_dimension(legacy_data))
    risk_level = normalize_risk_level(getattr(test_case, "risk_level", None), priority)
    coverage_tag = normalize_coverage_tag(getattr(test_case, "coverage_tag", None), case_type)
    ai_metadata = _dict_or_empty(getattr(test_case, "ai_metadata", None))
    if not ai_metadata and legacy_variables:
        ai_metadata = dict(legacy_variables)
    created_at = getattr(test_case, "created_at", None)
    updated_at = getattr(test_case, "updated_at", None)

    return {
        "id": test_case.id,
        "project_id": test_case.project_id,
        "api_endpoint_id": getattr(test_case, "api_endpoint_id", None),
        "name": test_case.name,
        "description": getattr(test_case, "description", None),
        "endpoint": endpoint_data,
        "endpoint_name": endpoint_data["name"],
        "endpoint_path": endpoint_data["path"],
        "type": case_type,
        "priority": priority,
        "status": status,
        "request": request_data,
        "request_data": request_data,
        "assertions": assertions,
        "dsl_assertions": dsl_assertions,
        "coverage_tag": coverage_tag,
        "risk_level": risk_level,
        "data_dependency": _dict_or_empty(getattr(test_case, "data_dependency", None)),
        "ai_metadata": ai_metadata,
        "timestamps": {
            "created_at": _iso_or_none(created_at),
            "updated_at": _iso_or_none(updated_at),
        },
        "created_at": created_at,
        "updated_at": updated_at,
    }


def validate_unified_model(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if normalize_type(data.get("type")) not in TEST_CASE_TYPES:
        errors.append("type is invalid")
    if normalize_priority(data.get("priority")) not in TEST_CASE_PRIORITIES:
        errors.append("priority is invalid")
    if normalize_status(data.get("status")) not in TEST_CASE_STATUSES:
        errors.append("status is invalid")
    if normalize_risk_level(data.get("risk_level"), data.get("priority")) not in RISK_LEVELS:
        errors.append("risk_level is invalid")
    request = data.get("request") or data.get("request_data")
    if not isinstance(request, dict):
        errors.append("request must be an object")
    for field in ("query", "headers", "body"):
        if not isinstance((request or {}).get(field), dict):
            errors.append(f"request.{field} must be an object")
    if not isinstance(data.get("assertions"), list):
        errors.append("assertions must be an array")
    if not isinstance(data.get("dsl_assertions"), list):
        errors.append("dsl_assertions must be an array")
    return errors


def normalize_type(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if raw in TEST_CASE_TYPES:
        return raw
    return LEGACY_TYPE_MAP.get(raw, "functional")


def normalize_priority(value: Any, risk_level: Any | None = None) -> str:
    raw = str(value or "").strip()
    upper = raw.upper()
    if upper in TEST_CASE_PRIORITIES:
        return upper
    lowered = raw.lower()
    if lowered in LEGACY_PRIORITY_MAP:
        return LEGACY_PRIORITY_MAP[lowered]
    risk = str(risk_level or "").strip().lower()
    if risk in RISK_TO_PRIORITY:
        return RISK_TO_PRIORITY[risk]
    return "P1"


def normalize_status(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if raw in TEST_CASE_STATUSES:
        return raw
    return LEGACY_STATUS_MAP.get(raw, "generated")


def normalize_risk_level(value: Any, priority: Any | None = None) -> str:
    raw = str(value or "").strip().lower()
    if raw in RISK_LEVELS:
        return raw
    if raw in {"p0", "p1", "p2"}:
        return PRIORITY_TO_RISK[raw.upper()]
    return PRIORITY_TO_RISK.get(normalize_priority(priority), "medium")


def normalize_request_data(value: Any, data: dict[str, Any] | None = None, endpoint: Any | None = None) -> dict[str, Any]:
    if isinstance(value, dict):
        request = dict(value)
    else:
        request = _request_from_legacy_steps((data or {}).get("steps"))

    path_params = request.get("path_params") if isinstance(request.get("path_params"), dict) else request.get("path")
    return {
        "method": str(request.get("method") or getattr(endpoint, "method", None) or "GET").upper(),
        "path": str(request.get("url_path") or request.get("path_url") or getattr(endpoint, "path", None) or request.get("path") or "/"),
        "headers": _dict_or_empty(request.get("headers")),
        "query": _dict_or_empty(request.get("query")),
        "path_params": _dict_or_empty(path_params),
        "body": _dict_or_empty(request.get("body")),
    }


def normalize_dsl_assertions(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [line.strip() for line in value.splitlines() if line.strip()]
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str):
            text = " ".join(item.strip().split())
            if text:
                result.append(text)
        elif isinstance(item, dict):
            text = item.get("dsl") or item.get("expression")
            if isinstance(text, str) and text.strip():
                result.append(" ".join(text.strip().split()))
    return result


def normalize_structured_assertions(raw_assertions: Any, dsl_assertions: list[str]) -> list[dict[str, Any]]:
    if isinstance(raw_assertions, list) and raw_assertions and all(isinstance(item, dict) for item in raw_assertions):
        return [_normalize_assertion_item(item) for item in raw_assertions]

    structured: list[dict[str, Any]] = []
    for index, dsl in enumerate(dsl_assertions, start=1):
        try:
            parsed = parse_assertion_dsl(dsl, source="user", enabled=True)
        except ValueError:
            continue
        structured.append(
            {
                "type": "status_code" if parsed.get("type") == "status_code" else parsed.get("type", "json_path"),
                "path": parsed.get("path"),
                "operator": parsed.get("operator"),
                "expression": dsl,
                "expected": parsed.get("expected"),
                "description": f"DSL断言 {index}",
            }
        )
    return structured


def normalize_coverage_tag(value: Any, case_type: str) -> list[str]:
    tags = [item for item in value if isinstance(item, str)] if isinstance(value, list) else []
    if case_type not in tags:
        tags.insert(0, case_type)
    return tags


def normalize_legacy_variables(data: dict[str, Any]) -> dict[str, Any]:
    variables = _dict_or_empty(data.get("variables"))
    variables["case_type"] = data["type"]
    variables["coverage_dimension"] = data["type"]
    variables["risk_level"] = data["priority"]
    variables["ai_assertion_dsl"] = list(data["dsl_assertions"])
    variables["unified_model_version"] = "v1"
    return variables


def normalize_legacy_steps(data: dict[str, Any]) -> list[dict[str, Any]]:
    request = dict(data["request_data"])
    return [{"name": f"{request.get('method', 'GET')} {request.get('path', '/')}", "request": request}]


def _normalize_assertion_item(item: dict[str, Any]) -> dict[str, Any]:
    assertion = dict(item)
    assertion_type = str(assertion.get("type") or "json_path")

    if assertion_type == "jsonpath":
        assertion_type = "json_path"
    elif assertion_type == "json_path_equal":
        assertion_type = "json_path"
        assertion["operator"] = "=="
    elif assertion_type == "json_path_not_null":
        assertion_type = "json_path"
        assertion["operator"] = "exists"
    elif assertion_type == "json_path_not_empty":
        assertion_type = "json_path"
        assertion["operator"] = "!="
        assertion.setdefault("expected", None)
    elif assertion_type == "json_path_contains":
        assertion_type = "json_path"
        assertion["operator"] = "contains"
    elif assertion_type == "business_success":
        assertion_type = "json_path"
        assertion.setdefault("path", "$.success")
        assertion["operator"] = "=="
        assertion.setdefault("expected", True)

    assertion["type"] = assertion_type
    assertion.setdefault("operator", "<=" if assertion_type == "response_time" else "==")
    if assertion_type == "business_code":
        assertion.setdefault("path", "$.code")

    expression = assertion.get("expression") or assertion.get("dsl")
    if not expression:
        try:
            expression = assertion_to_dsl(assertion)
        except ValueError:
            expression = ""

    normalized = {
        "type": assertion_type,
        "path": assertion.get("path"),
        "operator": assertion.get("operator"),
        "expression": str(expression),
        "expected": assertion.get("expected"),
        "description": str(assertion.get("description") or assertion.get("message") or ""),
    }
    for extra_key in ("id", "source", "priority", "enabled", "success_codes", "success_expression", "confidence"):
        if extra_key in assertion:
            normalized[extra_key] = assertion[extra_key]
    return normalized


def _request_from_legacy_steps(steps: Any) -> dict[str, Any]:
    if isinstance(steps, list) and steps:
        first = steps[0]
        if isinstance(first, dict) and isinstance(first.get("request"), dict):
            return dict(first["request"])
    return {}


def _legacy_coverage_dimension(data: dict[str, Any]) -> str | None:
    variables = _dict_or_empty(data.get("variables"))
    return variables.get("coverage_dimension") or variables.get("case_type")


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _orm_to_dict(test_case: Any) -> dict[str, Any]:
    return {
        "steps": getattr(test_case, "steps", None),
        "variables": getattr(test_case, "variables", None),
        "request_data": getattr(test_case, "request_data", None),
    }


def _iso_or_none(value: Any) -> str | None:
    if isinstance(value, datetime):
        return value.isoformat()
    return None
