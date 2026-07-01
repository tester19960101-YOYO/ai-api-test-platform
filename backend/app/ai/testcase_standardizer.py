from typing import Any

from app.core.assertion_dsl import parse_assertion_dsl
from app.models.api_endpoint import ApiEndpoint
from app.services.coverage_engine import (
    COVERAGE_DIMENSIONS,
    COVERAGE_TO_STRATEGY_CATEGORY,
    coverage_targets,
    required_coverage_dimensions,
)


VALID_CASE_TYPES = {"normal", "error", "boundary", "security"}
CASE_TYPE_ORDER = ("normal", "error", "boundary", "security")


class TestcaseStandardizationError(ValueError):
    pass


def standardize_ai_testcases(
    raw_output: dict[str, Any], endpoint: ApiEndpoint, coverage_plan: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Normalize model output into the platform's executable test_case structure."""

    raw_cases = _extract_raw_cases(raw_output)
    if not isinstance(raw_cases, list) or not raw_cases:
        raise TestcaseStandardizationError("AI output requires non-empty test_strategy or test_cases")

    raw_cases = _complete_coverage_cases(raw_cases, endpoint, coverage_plan)
    cases = [_standardize_case(item, endpoint, index) for index, item in enumerate(raw_cases, start=1)]
    case_types = {case["case_type"] for case in cases}
    missing = VALID_CASE_TYPES - case_types
    if missing:
        raise TestcaseStandardizationError(f"AI output missing case types: {sorted(missing)}")
    coverage_summary = _validate_coverage(cases, coverage_plan)
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
        "coverage_matrix": coverage_plan.get("coverage_matrix") if isinstance(coverage_plan, dict) else None,
        "coverage_summary": coverage_summary,
    }


def _extract_raw_cases(raw_output: dict[str, Any]) -> list[Any]:
    strategy = raw_output.get("test_strategy")
    if isinstance(strategy, dict):
        cases: list[Any] = []
        for category in CASE_TYPE_ORDER:
            items = strategy.get(category)
            if items is None:
                items = []
            if not isinstance(items, list):
                raise TestcaseStandardizationError(f"AI output test_strategy.{category} must be an array")
            for item in items:
                if isinstance(item, dict):
                    normalized = dict(item)
                    normalized.setdefault("type", category)
                    normalized.setdefault("strategy_category", category)
                    cases.append(normalized)
                else:
                    cases.append(item)
        return cases
    return raw_output.get("test_cases")


def _standardize_case(raw_case: Any, endpoint: ApiEndpoint, index: int) -> dict[str, Any]:
    if not isinstance(raw_case, dict):
        raise TestcaseStandardizationError(f"test case #{index} must be an object")

    case_type = str(raw_case.get("type") or raw_case.get("case_type") or "").strip().lower()
    if case_type not in VALID_CASE_TYPES:
        raise TestcaseStandardizationError(f"test case #{index} has invalid type: {case_type}")

    name = str(raw_case.get("name") or f"{endpoint.name}-{case_type}").strip()
    purpose = _required_text(raw_case, "purpose", index)
    reason = _required_text(raw_case, "reason", index)
    risk_level = _normalize_risk_level(raw_case.get("risk_level"), index)
    coverage_dimension = _normalize_coverage_dimension(raw_case.get("coverage_dimension"), index)
    request = _normalize_request(raw_case.get("request"), endpoint, index)
    assertions = _normalize_assertions(raw_case.get("assertions"), index, coverage_dimension)
    description = raw_case.get("description") or purpose

    return {
        "name": name[:128],
        "case_type": case_type,
        "description": str(description),
        "priority": risk_level,
        "steps": [{"name": f"{request['method']} {request['path']}", "request": request}],
        "assertions": assertions,
        "variables": {
            "generated_by": "ai_strategy_generator",
            "source": "ai_generated",
            "case_type": case_type,
            "source_endpoint_id": endpoint.id,
            "standardized": True,
            "purpose": purpose,
            "reason": reason,
            "risk_level": risk_level,
            "strategy_category": str(raw_case.get("strategy_category") or case_type),
            "coverage_dimension": coverage_dimension,
            "coverage_source": str(raw_case.get("coverage_source") or "ai"),
        },
    }


def _complete_coverage_cases(
    raw_cases: list[Any], endpoint: ApiEndpoint, coverage_plan: dict[str, Any] | None
) -> list[Any]:
    targets = coverage_targets(coverage_plan)
    completed = list(raw_cases)
    counts = {dimension: 0 for dimension in COVERAGE_DIMENSIONS}
    for raw_case in completed:
        if isinstance(raw_case, dict):
            dimension = str(raw_case.get("coverage_dimension") or "").strip().lower()
            if dimension in counts:
                counts[dimension] += 1

    for dimension in COVERAGE_DIMENSIONS:
        minimum = targets.get(dimension, {}).get("min", 1)
        while counts[dimension] < minimum:
            completed.append(_build_coverage_case(endpoint, dimension, counts[dimension] + 1))
            counts[dimension] += 1
    return completed


def _build_coverage_case(endpoint: ApiEndpoint, dimension: str, sequence: int) -> dict[str, Any]:
    category = COVERAGE_TO_STRATEGY_CATEGORY[dimension]
    request = _default_request(endpoint)
    request = _mutate_request_for_dimension(request, dimension, sequence)
    return {
        "name": f"{endpoint.name}-{dimension}-{sequence}",
        "type": category,
        "strategy_category": category,
        "coverage_dimension": dimension,
        "coverage_source": "coverage_engine",
        "purpose": _coverage_purpose(dimension),
        "request": request,
        "assertions": _coverage_assertions(dimension),
        "risk_level": _coverage_risk_level(dimension),
        "reason": _coverage_reason(dimension),
    }


def _default_request(endpoint: ApiEndpoint) -> dict[str, Any]:
    example_request = endpoint.example_request if isinstance(endpoint.example_request, dict) else {}
    request_params = endpoint.request_params if isinstance(endpoint.request_params, dict) else {}
    return {
        "headers": _extract_values(endpoint.headers or request_params.get("header") or {}),
        "query": _extract_values(request_params.get("query") or {}),
        "path": _extract_values(request_params.get("path") or {}),
        "body": example_request.get("body") if isinstance(example_request.get("body"), dict) else {},
    }


def _extract_values(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, Any] = {}
    for key, item in value.items():
        if isinstance(item, dict):
            result[key] = item.get("value", item.get("example", item.get("default", "")))
        else:
            result[key] = item
    return result


def _mutate_request_for_dimension(request: dict[str, Any], dimension: str, sequence: int) -> dict[str, Any]:
    mutated = {
        "headers": dict(request.get("headers") or {}),
        "query": dict(request.get("query") or {}),
        "path": dict(request.get("path") or {}),
        "body": dict(request.get("body") or {}),
    }
    if dimension == "validation":
        _mutate_first_field(mutated, "", sequence)
    elif dimension == "boundary":
        _mutate_first_field(mutated, 0 if sequence == 1 else 2147483647, sequence)
    elif dimension == "negative":
        _mutate_first_field(mutated, "../invalid" if sequence == 1 else None, sequence)
    elif dimension == "security":
        mutated["headers"].pop("Authorization", None)
        mutated["headers"].pop("authorization", None)
        mutated["headers"].pop("Cookie", None)
        mutated["headers"].pop("cookie", None)
    return mutated


def _mutate_first_field(request: dict[str, Any], value: Any, sequence: int) -> None:
    for section in ("path", "query", "body"):
        target = request.get(section)
        if isinstance(target, dict) and target:
            first_key = next(iter(target))
            target[first_key] = value
            return
    request["query"][f"coverage_probe_{sequence}"] = value


def _coverage_assertions(dimension: str) -> list[str]:
    if dimension in {"functional", "business", "dependency", "boundary"}:
        return ["status_code == 200", "$.data != null"]
    if dimension == "security":
        return ["status_code == 401"]
    return ["status_code == 400"]


def _coverage_risk_level(dimension: str) -> str:
    if dimension == "security":
        return "P0"
    if dimension in {"validation", "negative", "business"}:
        return "P1"
    return "P2"


def _coverage_purpose(dimension: str) -> str:
    return {
        "functional": "覆盖接口主功能成功路径。",
        "validation": "覆盖参数校验失败路径。",
        "boundary": "覆盖边界值输入。",
        "negative": "覆盖异常请求路径。",
        "security": "覆盖未授权或越权访问风险。",
        "business": "覆盖 HTTP 成功但业务语义失败的风险。",
        "dependency": "覆盖接口对已有数据或上游数据的依赖。",
    }[dimension]


def _coverage_reason(dimension: str) -> str:
    return {
        "functional": "主流程是接口最核心的可用性验证。",
        "validation": "参数校验缺失会导致脏数据或异常行为。",
        "boundary": "边界值容易暴露范围和类型处理缺陷。",
        "negative": "异常路径必须返回可控错误而不是系统异常。",
        "security": "安全场景缺失会造成高风险访问问题。",
        "business": "业务语义断言可以避免 HTTP 200 被误判为成功。",
        "dependency": "数据依赖不满足时容易导致不稳定或误判。",
    }[dimension]


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


def _normalize_assertions(raw_assertions: Any, index: int, coverage_dimension: str) -> list[str]:
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
    valid_assertions: list[str] = []
    for assertion in assertions:
        try:
            parse_assertion_dsl(assertion, source="ai", enabled=False)
            valid_assertions.append(assertion)
        except ValueError:
            continue
    return valid_assertions or _coverage_assertions(coverage_dimension)


def _dict_or_empty(value: Any, index: int, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TestcaseStandardizationError(f"test case #{index} request.{field_name} must be an object")
    return value


def _required_text(raw_case: dict[str, Any], field_name: str, index: int) -> str:
    value = raw_case.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise TestcaseStandardizationError(f"test case #{index} requires {field_name}")
    return value.strip()


def _normalize_risk_level(value: Any, index: int) -> str:
    risk_level = str(value or "").strip().upper()
    if risk_level not in {"P0", "P1", "P2"}:
        raise TestcaseStandardizationError(f"test case #{index} risk_level must be P0, P1, or P2")
    return risk_level


def _normalize_coverage_dimension(value: Any, index: int) -> str:
    coverage_dimension = str(value or "").strip().lower()
    if coverage_dimension not in COVERAGE_DIMENSIONS:
        raise TestcaseStandardizationError(
            f"test case #{index} coverage_dimension must be one of: {list(COVERAGE_DIMENSIONS)}"
        )
    return coverage_dimension


def _validate_coverage(cases: list[dict[str, Any]], coverage_plan: dict[str, Any] | None) -> dict[str, Any]:
    required_dimensions = required_coverage_dimensions(coverage_plan)
    targets = coverage_targets(coverage_plan)
    counts = {dimension: 0 for dimension in COVERAGE_DIMENSIONS}
    for case in cases:
        dimension = case.get("variables", {}).get("coverage_dimension")
        if dimension in counts:
            counts[dimension] += 1

    missing = [dimension for dimension in required_dimensions if counts.get(dimension, 0) == 0]
    if missing:
        raise TestcaseStandardizationError(f"AI output missing coverage dimensions: {missing}")

    under_target = [
        dimension
        for dimension in required_dimensions
        if counts.get(dimension, 0) < targets.get(dimension, {}).get("min", 1)
    ]
    if under_target:
        raise TestcaseStandardizationError(f"AI output does not meet coverage minimums: {under_target}")

    return {
        "required_dimensions": sorted(required_dimensions),
        "counts": counts,
        "missing_dimensions": [],
    }
