from typing import Any

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}


def parse_openapi_document(document: dict[str, Any]) -> dict[str, Any]:
    paths = document.get("paths")
    if not isinstance(paths, dict):
        raise ValueError("OpenAPI document must contain paths")

    global_security = document.get("security")
    endpoints: list[dict[str, Any]] = []

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        path_parameters = path_item.get("parameters", [])
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            endpoints.append(_parse_operation(path, method.upper(), operation, path_parameters, global_security))

    return {
        "version": document.get("openapi") or document.get("swagger"),
        "title": (document.get("info") or {}).get("title"),
        "endpoint_count": len(endpoints),
        "endpoints": endpoints,
    }


def _parse_operation(
    path: str,
    method: str,
    operation: dict[str, Any],
    path_parameters: list[dict[str, Any]],
    global_security: Any,
) -> dict[str, Any]:
    tags = operation.get("tags") if isinstance(operation.get("tags"), list) else []
    parameters = list(path_parameters) + list(operation.get("parameters") or [])
    headers = _parameters_by_location(parameters, "header")
    query_params = _parameters_by_location(parameters, "query")
    path_params = _parameters_by_location(parameters, "path")
    request_body = _parse_request_body(operation.get("requestBody"))
    response = _parse_response(operation.get("responses") or {})
    auth_required = bool(operation.get("security") or global_security)

    return {
        "name": operation.get("summary") or operation.get("operationId") or f"{method} {path}",
        "group_name": tags[0] if tags else None,
        "method": method,
        "path": path,
        "description": operation.get("description"),
        "headers": headers or None,
        "request_params": {
            "query": query_params,
            "path": path_params,
        },
        "request_body_schema": request_body.get("schema"),
        "response_schema": response.get("schema"),
        "example_request": {
            "method": method,
            "path": path,
            "headers": _example_values(headers),
            "query": _example_values(query_params),
            "path_params": _example_values(path_params),
            "body": request_body.get("example"),
        },
        "example_response": response.get("example"),
        "auth_required": auth_required,
        "tags": tags,
    }


def _parameters_by_location(parameters: list[dict[str, Any]], location: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for parameter in parameters:
        if not isinstance(parameter, dict) or parameter.get("in") != location:
            continue
        name = parameter.get("name")
        if not name:
            continue
        result[name] = {
            "required": parameter.get("required", False),
            "schema": parameter.get("schema") or {"type": parameter.get("type")},
            "description": parameter.get("description"),
            "example": parameter.get("example"),
        }
    return result


def _parse_request_body(request_body: Any) -> dict[str, Any]:
    if not isinstance(request_body, dict):
        return {"schema": None, "example": None}
    content = request_body.get("content") or {}
    media = _first_json_like_media(content)
    if not isinstance(media, dict):
        return {"schema": request_body, "example": None}
    return {
        "schema": media.get("schema"),
        "example": media.get("example") or _first_named_example(media.get("examples")),
    }


def _parse_response(responses: dict[str, Any]) -> dict[str, Any]:
    response = None
    for status_code in sorted(responses):
        if str(status_code).startswith("2"):
            response = responses[status_code]
            break
    if response is None and responses:
        response = next(iter(responses.values()))
    if not isinstance(response, dict):
        return {"schema": None, "example": None}
    content = response.get("content") or {}
    media = _first_json_like_media(content)
    if isinstance(media, dict):
        return {
            "schema": media.get("schema"),
            "example": media.get("example") or _first_named_example(media.get("examples")),
        }
    return {"schema": response.get("schema"), "example": response.get("example")}


def _first_json_like_media(content: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(content, dict):
        return None
    for media_type in ("application/json", "application/*+json", "*/*"):
        if isinstance(content.get(media_type), dict):
            return content[media_type]
    for media in content.values():
        if isinstance(media, dict):
            return media
    return None


def _first_named_example(examples: Any) -> Any:
    if not isinstance(examples, dict) or not examples:
        return None
    example = next(iter(examples.values()))
    if isinstance(example, dict) and "value" in example:
        return example["value"]
    return example


def _example_values(parameters: dict[str, Any]) -> dict[str, Any]:
    values = {}
    for name, metadata in parameters.items():
        values[name] = metadata.get("example")
    return values
