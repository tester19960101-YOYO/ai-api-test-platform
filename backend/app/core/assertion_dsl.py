from __future__ import annotations

import re
from typing import Any


SUPPORTED_OPERATORS = ("not null", "contains", "exists", "==", "!=", ">", "<")


def parse_assertion_dsl(dsl: str, source: str = "user", enabled: bool | None = None) -> dict[str, Any]:
    text = " ".join(str(dsl or "").strip().split())
    if not text:
        raise ValueError("DSL cannot be empty")

    left, operator, expected_text = _split_dsl(text)
    assertion_type = "status_code" if left == "status_code" else "json_path"
    result: dict[str, Any] = {
        "source": source,
        "type": assertion_type,
        "path": None if left == "status_code" else left,
        "operator": "exists" if operator == "not null" else operator,
        "expected": _parse_expected(expected_text, operator),
        "enabled": source != "ai" if enabled is None else enabled,
        "dsl": text,
    }
    if left == "$.code" and operator == "==" and isinstance(result["expected"], int):
        result["type"] = "business_code"
        result["success_codes"] = [result["expected"]]
    return result


def assertion_to_dsl(assertion: Any) -> str:
    if isinstance(assertion, str):
        return " ".join(assertion.strip().split())
    if not isinstance(assertion, dict):
        raise ValueError("assertion must be string or object")

    if isinstance(assertion.get("dsl"), str) and assertion["dsl"].strip():
        return " ".join(assertion["dsl"].strip().split())

    assertion_type = str(assertion.get("type") or "json_path")
    path = assertion.get("path")
    operator = assertion.get("operator")
    expected = assertion.get("expected")

    if assertion_type == "status_code":
        return f"status_code {operator or '=='} {_format_expected(expected)}"
    if assertion_type == "business_code":
        if expected is None and isinstance(assertion.get("success_codes"), list) and assertion["success_codes"]:
            expected = assertion["success_codes"][0]
        return f"{path or '$.code'} {operator or '=='} {_format_expected(expected)}"

    if assertion_type == "json_path_equal":
        operator = "=="
    elif assertion_type == "json_path_contains":
        operator = "contains"
    elif assertion_type in {"json_path_not_null", "json_path_not_empty"}:
        operator = "not null"
    elif assertion_type == "business_success":
        path = path or "$.success"
        operator = operator or "=="
        expected = True if expected is None else expected

    operator = operator or "=="
    if operator == "exists":
        return f"{path} exists"
    if operator == "!=" and expected is None:
        return f"{path} != null"
    if operator == "not null":
        return f"{path} not null"
    return f"{path} {operator} {_format_expected(expected)}"


def parse_assertion_dsl_list(items: Any, source: str = "user", enabled: bool | None = None) -> list[dict[str, Any]]:
    if not isinstance(items, list):
        return []
    parsed: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, str):
            parsed.append(parse_assertion_dsl(item, source=source, enabled=enabled))
        elif isinstance(item, dict):
            parsed.append(item)
    return parsed


def assertions_to_dsl_list(items: Any) -> list[str]:
    if not isinstance(items, list):
        return []
    result: list[str] = []
    for item in items:
        try:
            result.append(assertion_to_dsl(item))
        except ValueError:
            continue
    return result


def _split_dsl(text: str) -> tuple[str, str, str | None]:
    for operator in SUPPORTED_OPERATORS:
        pattern = rf"^(.+?)\s+{re.escape(operator)}(?:\s+(.+))?$"
        match = re.match(pattern, text)
        if match:
            left = match.group(1).strip()
            expected = match.group(2).strip() if match.group(2) is not None else None
            if operator in {"==", "!=", ">", "<", "contains"} and expected is None:
                raise ValueError(f"{operator} requires expected value")
            _validate_left(left)
            return left, operator, expected
    raise ValueError("unsupported DSL expression")


def _validate_left(left: str) -> None:
    if left == "status_code":
        return
    if left.startswith("$."):
        return
    raise ValueError("left side must be status_code or JSONPath starting with $.")


def _parse_expected(value: str | None, operator: str) -> Any:
    if operator in {"exists", "not null"}:
        return None
    if value is None:
        return None
    lowered = value.lower()
    if lowered == "null":
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def _format_expected(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
