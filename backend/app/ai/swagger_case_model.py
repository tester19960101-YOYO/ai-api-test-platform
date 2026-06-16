from typing import Any

from app.models.api_endpoint import ApiEndpoint


def build_endpoint_model(endpoint: ApiEndpoint) -> dict[str, Any]:
    """Build a compact structured model from the stored Swagger/OpenAPI endpoint asset."""

    return {
        "id": endpoint.id,
        "name": endpoint.name,
        "group_name": endpoint.group_name,
        "method": endpoint.method.upper(),
        "path": endpoint.path,
        "description": endpoint.description,
        "auth_required": endpoint.auth_required,
        "headers": endpoint.headers or {},
        "request_params": endpoint.request_params or {},
        "request_body_schema": endpoint.request_body_schema or {},
        "response_schema": endpoint.response_schema or {},
        "example_request": endpoint.example_request or {},
        "example_response": endpoint.example_response or {},
        "tags": endpoint.tags or [],
    }
