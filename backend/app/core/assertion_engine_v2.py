from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from app.core.assertion_dsl import parse_assertion_dsl


SOURCE_PRIORITY = {
    "user": 1,
    "swagger": 2,
    "ai": 3,
}


@dataclass(frozen=True)
class AssertionInput:
    swagger: list[dict[str, Any]]
    ai: list[dict[str, Any]]
    user: list[dict[str, Any]]


def build_assertion(assertion: dict[str, Any], source: str, default_priority: int | None = None) -> dict[str, Any]:
    assertion_type = _normalize_type(str(assertion.get("type") or "json_path"))
    path = assertion.get("path")
    operator = assertion.get("operator") or _operator_from_legacy_type(assertion_type)
    expected = assertion.get("expected")
    normalized = {
        "id": str(assertion.get("id") or f"{source}-{uuid4().hex[:12]}"),
        "source": source,
        "type": _canonical_type(assertion_type),
        "path": path,
        "operator": operator,
        "expected": expected,
        "priority": int(assertion.get("priority") or default_priority or SOURCE_PRIORITY[source]),
        "enabled": bool(assertion.get("enabled", source != "ai")),
    }
    if "success_codes" in assertion:
        normalized["success_codes"] = assertion["success_codes"]
    if "success_expression" in assertion:
        normalized["success_expression"] = assertion["success_expression"]
    if "confidence" in assertion:
        normalized["confidence"] = assertion["confidence"]
    if "dsl" in assertion:
        normalized["dsl"] = assertion["dsl"]
    return normalized


def build_swagger_assertions(endpoint: Any, success_codes: list[int] | None = None) -> list[dict[str, Any]]:
    success_codes = success_codes or [200, 0]
    response_schema = _as_dict(getattr(endpoint, "response_schema", None))
    example_response = _as_dict(getattr(endpoint, "example_response", None))
    assertions: list[dict[str, Any]] = [
        build_assertion(
            {
                "id": "swagger-status-code",
                "type": "status_code",
                "operator": "==",
                "expected": 200,
            },
            "swagger",
        )
    ]

    if "code" in example_response or "code" in _schema_properties(response_schema):
        expected = example_response.get("code") if "code" in example_response else success_codes
        assertions.append(
            build_assertion(
                {
                    "id": "swagger-business-code",
                    "type": "business_code",
                    "path": "$.code",
                    "operator": "==",
                    "expected": expected,
                    "success_codes": success_codes,
                },
                "swagger",
            )
        )
    if "success" in example_response or "success" in _schema_properties(response_schema):
        assertions.append(
            build_assertion(
                {
                    "id": "swagger-business-success",
                    "type": "json_path",
                    "path": "$.success",
                    "operator": "==",
                    "expected": True,
                },
                "swagger",
            )
        )

    required_paths = _required_paths(response_schema)
    for path in required_paths:
        assertions.append(
            build_assertion(
                {
                    "id": f"swagger-required-{path}",
                    "type": "json_path",
                    "path": path,
                    "operator": "exists",
                },
                "swagger",
            )
        )
    return assertions


def normalize_ai_suggestions(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, dict):
        return []
    suggestions = raw.get("assertions") or raw.get("suggestions")
    if not isinstance(suggestions, list):
        return []
    normalized: list[dict[str, Any]] = []
    for item in suggestions:
        if isinstance(item, str):
            normalized.append(build_assertion(parse_assertion_dsl(item, source="ai", enabled=False), "ai"))
        elif isinstance(item, dict):
            normalized.append(build_assertion(_legacy_to_v2(item), "ai"))
    return normalized


def normalize_user_assertions(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    normalized: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, str):
            normalized.append(build_assertion(parse_assertion_dsl(item, source="user", enabled=True), "user"))
        elif isinstance(item, dict):
            normalized.append(build_assertion(_legacy_to_v2(item), "user"))
    return normalized


def fuse_assertions(
    swagger_assertions: list[dict[str, Any]] | None = None,
    ai_assertions: list[dict[str, Any]] | None = None,
    user_assertions: list[dict[str, Any]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    collected: list[dict[str, Any]] = []
    for source, assertions in (
        ("swagger", swagger_assertions or []),
        ("ai", ai_assertions or []),
        ("user", user_assertions or []),
    ):
        for assertion in assertions:
            source_name = assertion.get("source") or source
            collected.append(build_assertion(assertion, source_name))

    collected.sort(key=lambda item: (item["priority"], SOURCE_PRIORITY.get(item["source"], 99)))
    deduped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for assertion in collected:
        key = _dedupe_key(assertion)
        if key not in deduped:
            deduped[key] = assertion

    return {"final_assertions": list(deduped.values())}


def _dedupe_key(assertion: dict[str, Any]) -> tuple[str, str, str]:
    if assertion.get("type") == "status_code":
        return ("status_code", "__http__", "==")
    if assertion.get("type") == "response_time":
        return ("response_time", "__response_time__", assertion.get("operator") or "<=")
    return ("path", assertion.get("path") or "__unknown__", assertion.get("operator") or "==")


def _legacy_to_v2(assertion: dict[str, Any]) -> dict[str, Any]:
    assertion_type = str(assertion.get("type") or "")
    result = dict(assertion)
    if assertion_type == "json_path_equal":
        result["type"] = "json_path"
        result["operator"] = "=="
    elif assertion_type == "json_path_not_null":
        result["type"] = "json_path"
        result["operator"] = "exists"
    elif assertion_type == "json_path_not_empty":
        result["type"] = "json_path"
        result["operator"] = "!="
        result.setdefault("expected", None)
    elif assertion_type == "json_path_contains":
        result["type"] = "json_path"
        result["operator"] = "contains"
    elif assertion_type == "business_success":
        result["type"] = "json_path"
        result.setdefault("path", "$.success")
        result["operator"] = "=="
        result.setdefault("expected", True)
    return result


def _normalize_type(assertion_type: str) -> str:
    return _legacy_to_v2({"type": assertion_type}).get("type", assertion_type)


def _canonical_type(assertion_type: str) -> str:
    if assertion_type in {"status_code", "business_code", "response_time"}:
        return assertion_type
    return "json_path"


def _operator_from_legacy_type(assertion_type: str) -> str:
    if assertion_type == "response_time":
        return "<="
    if assertion_type in {"status_code", "business_code", "json_path_equal"}:
        return "=="
    if assertion_type == "json_path_contains":
        return "contains"
    if assertion_type in {"json_path_not_null", "json_path_not_empty"}:
        return "exists"
    return "=="


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _schema_properties(schema: dict[str, Any]) -> dict[str, Any]:
    properties = schema.get("properties")
    return properties if isinstance(properties, dict) else {}


def _required_paths(schema: dict[str, Any], prefix: str = "$") -> list[str]:
    if not isinstance(schema, dict):
        return []
    paths: list[str] = []
    properties = _schema_properties(schema)
    required = schema.get("required")
    if isinstance(required, list):
        for name in required:
            if isinstance(name, str):
                paths.append(f"{prefix}.{name}")
    for name, child_schema in properties.items():
        if isinstance(child_schema, dict):
            paths.extend(_required_paths(child_schema, f"{prefix}.{name}"))
    return paths
