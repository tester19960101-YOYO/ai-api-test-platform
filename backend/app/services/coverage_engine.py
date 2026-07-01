from typing import Any


COVERAGE_DIMENSIONS = (
    "functional",
    "validation",
    "boundary",
    "negative",
    "security",
    "business",
    "dependency",
)

COVERAGE_TARGETS: dict[str, dict[str, int]] = {
    "functional": {"min": 1, "max": 2},
    "validation": {"min": 2, "max": 3},
    "boundary": {"min": 2, "max": 2},
    "negative": {"min": 2, "max": 3},
    "security": {"min": 1, "max": 2},
    "business": {"min": 1, "max": 1},
    "dependency": {"min": 1, "max": 1},
}

COVERAGE_TO_STRATEGY_CATEGORY = {
    "functional": "normal",
    "validation": "error",
    "boundary": "boundary",
    "negative": "error",
    "security": "security",
    "business": "normal",
    "dependency": "normal",
}


class CoverageEngine:
    """Build the mandatory coverage plan used to drive AI testcase generation."""

    def build_coverage_plan(self, api_schema: dict[str, Any]) -> dict[str, Any]:
        method = str(api_schema.get("method") or "").upper()
        auth_required = bool(api_schema.get("auth_required"))
        has_body = bool(api_schema.get("request_body_schema") or api_schema.get("example_request", {}).get("body"))
        request_params = api_schema.get("request_params") if isinstance(api_schema.get("request_params"), dict) else {}

        return {
            "coverage_matrix": {dimension: True for dimension in COVERAGE_DIMENSIONS},
            "coverage_targets": {
                dimension: {
                    **target,
                    "strategy_category": COVERAGE_TO_STRATEGY_CATEGORY[dimension],
                }
                for dimension, target in COVERAGE_TARGETS.items()
            },
            "coverage_context": {
                "method": method,
                "auth_required": auth_required,
                "has_body": has_body,
                "has_query_params": bool(request_params.get("query")),
                "has_path_params": bool(request_params.get("path")),
                "has_headers": bool(api_schema.get("headers") or request_params.get("header")),
            },
        }


def required_coverage_dimensions(coverage_plan: dict[str, Any] | None) -> set[str]:
    if not isinstance(coverage_plan, dict):
        return set(COVERAGE_DIMENSIONS)
    matrix = coverage_plan.get("coverage_matrix")
    if not isinstance(matrix, dict):
        return set(COVERAGE_DIMENSIONS)
    return {dimension for dimension in COVERAGE_DIMENSIONS if matrix.get(dimension) is True}


def coverage_targets(coverage_plan: dict[str, Any] | None) -> dict[str, dict[str, int]]:
    if not isinstance(coverage_plan, dict):
        return COVERAGE_TARGETS
    targets = coverage_plan.get("coverage_targets")
    if not isinstance(targets, dict):
        return COVERAGE_TARGETS
    normalized: dict[str, dict[str, int]] = {}
    for dimension in COVERAGE_DIMENSIONS:
        target = targets.get(dimension)
        if isinstance(target, dict):
            normalized[dimension] = {
                "min": int(target.get("min", COVERAGE_TARGETS[dimension]["min"])),
                "max": int(target.get("max", COVERAGE_TARGETS[dimension]["max"])),
            }
        else:
            normalized[dimension] = COVERAGE_TARGETS[dimension]
    return normalized
