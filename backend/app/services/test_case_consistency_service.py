from __future__ import annotations

from typing import Any

from app.services.test_case_unified_model import test_case_to_unified_dict, validate_unified_model


def check_test_case_unified_consistency(test_case: Any) -> dict[str, Any]:
    unified = test_case_to_unified_dict(test_case)
    errors = validate_unified_model(unified)
    if not unified.get("dsl_assertions"):
        errors.append("dsl_assertions is empty")
    if not unified.get("assertions"):
        errors.append("assertions is empty")
    if not unified.get("coverage_tag"):
        errors.append("coverage_tag is empty")
    endpoint = unified.get("endpoint") or {}
    for field in ("id", "name", "method", "path"):
        if endpoint.get(field) in (None, ""):
            errors.append(f"endpoint.{field} is missing")
    return {
        "valid": not errors,
        "errors": errors,
        "model_version": "TestCaseUnifiedModel v1",
    }


def summarize_test_case_consistency(test_cases: list[Any]) -> dict[str, Any]:
    items = [check_test_case_unified_consistency(test_case) for test_case in test_cases]
    invalid_count = sum(1 for item in items if not item["valid"])
    return {
        "total": len(items),
        "valid_count": len(items) - invalid_count,
        "invalid_count": invalid_count,
        "items": items,
    }
