from typing import Any

from app.models.api_endpoint import ApiEndpoint


class TestcaseGeneratorAgent:
    """Mock agent that converts an endpoint asset into structured testcase JSON."""

    model_name = "mock-testcase-generator"

    def generate(self, endpoint: ApiEndpoint) -> dict[str, Any]:
        request_template = self._build_request_template(endpoint)
        cases = [
            self._build_case(endpoint, "normal", "正常场景", 200, request_template),
            self._build_case(endpoint, "exception", "异常参数场景", 400, self._build_exception_request(request_template)),
            self._build_case(endpoint, "boundary", "边界值场景", 200, self._build_boundary_request(request_template)),
            self._build_case(endpoint, "auth", "鉴权场景", 401 if endpoint.auth_required else 200, self._build_auth_request(endpoint, request_template)),
        ]
        return {
            "model_name": self.model_name,
            "endpoint": {
                "id": endpoint.id,
                "name": endpoint.name,
                "method": endpoint.method,
                "path": endpoint.path,
                "auth_required": endpoint.auth_required,
            },
            "cases": cases,
        }

    def _build_case(
        self,
        endpoint: ApiEndpoint,
        case_type: str,
        title: str,
        expected_status_code: int,
        request_data: dict[str, Any],
    ) -> dict[str, Any]:
        assertions = [{"type": "status_code", "expected": expected_status_code}]
        if expected_status_code < 400:
            assertions.extend(
                [
                    *self._build_business_assertions(endpoint),
                    {"type": "json_path_not_null", "path": "$"},
                    {"type": "json_path_contains", "path": "$", "expected": self._response_keyword(endpoint)},
                ]
            )
        else:
            assertions.append({"type": "json_path_equal", "path": "$.code", "expected": expected_status_code})

        return {
            "name": f"{endpoint.name}-{title}",
            "case_type": case_type,
            "description": f"Mock AI 根据接口资产生成的{title}用例",
            "priority": "medium",
            "steps": [
                {
                    "name": f"请求 {endpoint.method.upper()} {endpoint.path}",
                    "request": request_data,
                }
            ],
            "assertions": assertions,
            "variables": {
                "generated_by": self.model_name,
                "case_type": case_type,
                "source_endpoint_id": endpoint.id,
            },
        }

    def _build_request_template(self, endpoint: ApiEndpoint) -> dict[str, Any]:
        request_params = endpoint.request_params or {}
        return {
            "method": endpoint.method.upper(),
            "path": endpoint.path,
            "headers": self._normalize_headers(endpoint.headers),
            "query": self._build_param_values(request_params.get("query")),
            "path_params": self._build_param_values(request_params.get("path")),
            "body": self._build_body(endpoint),
        }

    def _build_exception_request(self, request_data: dict[str, Any]) -> dict[str, Any]:
        data = self._copy_request(request_data)
        if data["query"]:
            first_key = next(iter(data["query"]))
            data["query"][first_key] = None
        elif data["body"]:
            data["body"]["__invalid__"] = True
        else:
            data["query"]["invalid"] = None
        return data

    def _build_boundary_request(self, request_data: dict[str, Any]) -> dict[str, Any]:
        data = self._copy_request(request_data)
        for container_name in ("query", "path_params", "body"):
            container = data.get(container_name)
            if isinstance(container, dict):
                for key, value in list(container.items()):
                    if isinstance(value, int):
                        container[key] = 0
                    elif isinstance(value, str):
                        container[key] = value[:128]
        if not data["query"] and not data["body"]:
            data["query"]["limit"] = 1
        return data

    def _build_auth_request(self, endpoint: ApiEndpoint, request_data: dict[str, Any]) -> dict[str, Any]:
        data = self._copy_request(request_data)
        if endpoint.auth_required:
            data["headers"].pop("Authorization", None)
        return data

    def _normalize_headers(self, headers: dict[str, Any] | None) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        for key, value in (headers or {}).items():
            if isinstance(value, dict):
                normalized[key] = value.get("example") or value.get("default") or "mock-value"
            else:
                normalized[key] = value
        return normalized

    def _build_param_values(self, params: Any) -> dict[str, Any]:
        if not isinstance(params, dict):
            return {}
        values: dict[str, Any] = {}
        for key, definition in params.items():
            if isinstance(definition, dict):
                values[key] = definition.get(
                    "value",
                    definition.get("example", self._example_from_schema(definition.get("schema") or definition)),
                )
            else:
                values[key] = definition
        return values

    def _build_body(self, endpoint: ApiEndpoint) -> dict[str, Any]:
        example_request = endpoint.example_request or {}
        if isinstance(example_request, dict) and isinstance(example_request.get("body"), dict):
            return example_request["body"]
        body_schema = endpoint.request_body_schema or {}
        if isinstance(body_schema, dict):
            if isinstance(body_schema.get("x-example"), dict):
                return body_schema["x-example"]
            if isinstance(body_schema.get("example"), dict):
                return body_schema["example"]
            properties = body_schema.get("properties")
            if isinstance(properties, dict):
                return {key: self._example_from_schema(value) for key, value in properties.items()}
            if "raw" in body_schema:
                return {"raw": body_schema["raw"]}
        return {}

    def _example_from_schema(self, schema: Any) -> Any:
        if not isinstance(schema, dict):
            return "mock-value"
        if "example" in schema:
            return schema["example"]
        schema_type = schema.get("type")
        if schema_type == "integer":
            return 1
        if schema_type == "number":
            return 1.0
        if schema_type == "boolean":
            return True
        if schema_type == "array":
            return []
        if schema_type == "object":
            return {}
        return "mock-value"

    def _response_keyword(self, endpoint: ApiEndpoint) -> str:
        if isinstance(endpoint.example_response, dict) and endpoint.example_response:
            return next(iter(endpoint.example_response.keys()))
        if isinstance(endpoint.response_schema, dict) and endpoint.response_schema:
            properties = endpoint.response_schema.get("properties")
            if isinstance(properties, dict) and properties:
                return next(iter(properties.keys()))
        return "success"

    def _build_business_assertions(self, endpoint: ApiEndpoint) -> list[dict[str, Any]]:
        assertions: list[dict[str, Any]] = []
        response_example = endpoint.example_response if isinstance(endpoint.example_response, dict) else {}
        response_schema = endpoint.response_schema if isinstance(endpoint.response_schema, dict) else {}
        properties = response_schema.get("properties") if isinstance(response_schema.get("properties"), dict) else {}

        if "code" in response_example or "code" in properties:
            expected = response_example.get("code", 200)
            assertions.append({"type": "business_code", "path": "$.code", "expected": expected})
        if "success" in response_example or "success" in properties:
            assertions.append({"type": "business_success", "path": "$.success", "expected": True})
        if "data" in response_example or "data" in properties:
            assertions.append({"type": "json_path_not_null", "path": "$.data"})
        return assertions

    def _copy_request(self, request_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "method": request_data["method"],
            "path": request_data["path"],
            "headers": dict(request_data.get("headers") or {}),
            "query": dict(request_data.get("query") or {}),
            "path_params": dict(request_data.get("path_params") or {}),
            "body": dict(request_data.get("body") or {}),
        }
