from copy import deepcopy
from typing import Any

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
JSON_MEDIA_TYPES = ("application/json", "application/*+json", "*/*")


def parse_openapi_document(document: dict[str, Any]) -> dict[str, Any]:
    paths = document.get("paths")
    if not isinstance(paths, dict):
        raise ValueError("OpenAPI document must contain paths")

    resolver = SchemaResolver(document)
    global_security = document.get("security")
    endpoints: list[dict[str, Any]] = []

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        path_parameters = path_item.get("parameters", [])
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            endpoints.append(
                _parse_operation(path, method.upper(), operation, path_parameters, global_security, resolver)
            )

    return {
        "version": document.get("openapi") or document.get("swagger"),
        "title": (document.get("info") or {}).get("title"),
        "endpoint_count": len(endpoints),
        "endpoints": endpoints,
    }


class SchemaResolver:
    def __init__(self, document: dict[str, Any]) -> None:
        self.document = document

    def resolve_schema(self, schema: Any, stack: set[str] | None = None) -> Any:
        if not isinstance(schema, dict):
            return schema
        stack = stack or set()
        if "$ref" in schema:
            ref = schema["$ref"]
            resolved = self._resolve_ref(ref)
            if resolved is None or ref in stack:
                return deepcopy(schema)
            merged = {key: value for key, value in schema.items() if key != "$ref"}
            expanded = self.resolve_schema(resolved, stack | {ref})
            if isinstance(expanded, dict):
                expanded = {**deepcopy(expanded), **merged}
                expanded["x-ref"] = ref
            return expanded

        result = deepcopy(schema)
        if isinstance(result.get("properties"), dict):
            result["properties"] = {
                key: self.resolve_schema(value, stack)
                for key, value in result["properties"].items()
            }
        if isinstance(result.get("items"), dict):
            result["items"] = self.resolve_schema(result["items"], stack)
        for keyword in ("allOf", "oneOf", "anyOf"):
            if isinstance(result.get(keyword), list):
                result[keyword] = [self.resolve_schema(item, stack) for item in result[keyword]]
            if keyword == "allOf" and isinstance(result.get(keyword), list):
                result = _merge_all_of(result)
        return result

    def _resolve_ref(self, ref: str) -> Any | None:
        if not ref.startswith("#/"):
            return None
        current: Any = self.document
        for part in ref[2:].split("/"):
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current


def _parse_operation(
    path: str,
    method: str,
    operation: dict[str, Any],
    path_parameters: list[dict[str, Any]],
    global_security: Any,
    resolver: SchemaResolver,
) -> dict[str, Any]:
    tags = operation.get("tags") if isinstance(operation.get("tags"), list) else []
    parameters = list(path_parameters) + list(operation.get("parameters") or [])
    parameter_data = _parse_parameters(parameters, resolver)
    request_body = _parse_request_body(operation.get("requestBody"), resolver)
    if request_body["schema"] is None:
        request_body = _parse_swagger_body_parameter(parameters, resolver)
    response = _parse_responses(operation.get("responses") or {}, resolver)
    auth_required = bool(operation.get("security") or global_security)

    return {
        "name": operation.get("summary") or operation.get("operationId") or f"{method} {path}",
        "group_name": tags[0] if tags else None,
        "summary": operation.get("summary"),
        "operation_id": operation.get("operationId"),
        "method": method,
        "path": path,
        "description": operation.get("description"),
        "headers": parameter_data["definitions"]["header"] or None,
        "request_params": parameter_data["definitions"],
        "request_body_schema": request_body["schema"],
        "response_schema": response["schema"],
        "example_request": {
            "method": method,
            "path": path,
            "headers": parameter_data["examples"]["header"],
            "query": parameter_data["examples"]["query"],
            "path_params": parameter_data["examples"]["path"],
            "cookies": parameter_data["examples"]["cookie"],
            "body": request_body["example"],
            "schema": {
                "parameters": parameter_data["definitions"],
                "body": request_body["schema"],
            },
        },
        "example_response": response["example"],
        "auth_required": auth_required,
        "tags": tags,
    }


def _parse_parameters(parameters: list[dict[str, Any]], resolver: SchemaResolver) -> dict[str, Any]:
    definitions = {"query": {}, "path": {}, "header": {}, "cookie": {}}
    examples = {"query": {}, "path": {}, "header": {}, "cookie": {}}

    for parameter in parameters:
        if not isinstance(parameter, dict):
            continue
        location = parameter.get("in")
        name = parameter.get("name")
        if location not in definitions or not name:
            continue
        raw_schema = parameter.get("schema") or _swagger_parameter_schema(parameter)
        schema = resolver.resolve_schema(raw_schema) if isinstance(raw_schema, dict) else raw_schema
        example = _first_defined(parameter.get("example"), parameter.get("default"), _example_from_schema(schema))
        definitions[location][name] = {
            "name": name,
            "in": location,
            "required": parameter.get("required", False),
            "type": _schema_type(schema),
            "description": parameter.get("description"),
            "example": parameter.get("example"),
            "default": parameter.get("default"),
            "schema": schema,
            "value": example,
        }
        examples[location][name] = example

    return {"definitions": definitions, "examples": examples}


def _parse_request_body(request_body: Any, resolver: SchemaResolver) -> dict[str, Any]:
    if not isinstance(request_body, dict):
        return {"schema": None, "example": None}
    content = request_body.get("content") or {}
    media = _first_json_like_media(content)
    if not isinstance(media, dict):
        schema = resolver.resolve_schema(request_body)
        return {"schema": schema, "example": _example_from_schema(schema)}

    raw_schema = media.get("schema")
    schema = resolver.resolve_schema(raw_schema) if isinstance(raw_schema, dict) else raw_schema
    explicit_example = media.get("example") or _first_named_example(media.get("examples"))
    example = _first_defined(explicit_example, _example_from_schema(schema))
    if isinstance(schema, dict):
        schema = {
            **schema,
            "x-media-type": _media_type(content, media),
            "x-required-body": bool(request_body.get("required", False)),
            "x-example": example,
            "x-raw-schema": raw_schema,
        }
    return {"schema": schema, "example": example}


def _parse_swagger_body_parameter(parameters: list[dict[str, Any]], resolver: SchemaResolver) -> dict[str, Any]:
    for parameter in parameters:
        if not isinstance(parameter, dict) or parameter.get("in") != "body":
            continue
        raw_schema = parameter.get("schema")
        schema = resolver.resolve_schema(raw_schema) if isinstance(raw_schema, dict) else raw_schema
        example = _first_defined(parameter.get("example"), parameter.get("default"), _example_from_schema(schema))
        if isinstance(schema, dict):
            schema = {
                **schema,
                "x-required-body": bool(parameter.get("required", False)),
                "x-example": example,
                "x-raw-schema": raw_schema,
            }
        return {"schema": schema, "example": example}
    return {"schema": None, "example": None}


def _parse_responses(responses: dict[str, Any], resolver: SchemaResolver) -> dict[str, Any]:
    response_examples: dict[str, Any] = {}
    response_schemas: dict[str, Any] = {}
    preferred_status = _preferred_response_status(responses)

    for status_code, response in responses.items():
        if not isinstance(response, dict):
            continue
        content = response.get("content") or {}
        media = _first_json_like_media(content)
        if isinstance(media, dict):
            raw_schema = media.get("schema")
            schema = resolver.resolve_schema(raw_schema) if isinstance(raw_schema, dict) else raw_schema
            explicit_example = media.get("example") or _first_named_example(media.get("examples"))
            example = _first_defined(explicit_example, _example_from_schema(schema))
        else:
            raw_schema = response.get("schema")
            schema = resolver.resolve_schema(raw_schema) if isinstance(raw_schema, dict) else raw_schema
            explicit_example = response.get("example") or _first_named_example(response.get("examples"))
            example = _first_defined(explicit_example, _example_from_schema(schema))
        response_schemas[str(status_code)] = {
            "description": response.get("description"),
            "schema": schema,
            "raw_schema": raw_schema,
            "example": example,
        }
        response_examples[str(status_code)] = example

    selected = response_schemas.get(preferred_status) or next(iter(response_schemas.values()), {})
    selected_schema = selected.get("schema")
    if isinstance(selected_schema, dict):
        selected_schema = {
            **selected_schema,
            "x-responses": response_schemas,
            "x-examples": response_examples,
            "x-preferred-status": preferred_status,
        }
    return {
        "schema": selected_schema,
        "example": response_examples.get(preferred_status) or selected.get("example"),
    }


def _swagger_parameter_schema(parameter: dict[str, Any]) -> dict[str, Any]:
    schema = {key: parameter.get(key) for key in ("type", "format", "items", "enum") if key in parameter}
    if parameter.get("default") is not None:
        schema["default"] = parameter["default"]
    if parameter.get("example") is not None:
        schema["example"] = parameter["example"]
    return schema or {"type": "string"}


def _example_from_schema(schema: Any) -> Any:
    if not isinstance(schema, dict):
        return None
    if "example" in schema:
        return schema["example"]
    if "default" in schema:
        return schema["default"]
    if "enum" in schema and isinstance(schema["enum"], list) and schema["enum"]:
        return schema["enum"][0]

    schema_type = _schema_type(schema)
    if schema_type == "integer":
        return 1
    if schema_type == "number":
        return 1
    if schema_type == "boolean":
        return False
    if schema_type == "array":
        return [_example_from_schema(schema.get("items"))]
    if schema_type == "object" or isinstance(schema.get("properties"), dict):
        required = set(schema.get("required") or [])
        result = {}
        for key, property_schema in (schema.get("properties") or {}).items():
            value = _example_from_schema(property_schema)
            if key in required or value is not None:
                result[key] = value
        return result
    return "string"


def _schema_type(schema: Any) -> str | None:
    if not isinstance(schema, dict):
        return None
    schema_type = schema.get("type")
    if isinstance(schema_type, str):
        return schema_type
    if isinstance(schema.get("properties"), dict):
        return "object"
    if isinstance(schema.get("items"), dict):
        return "array"
    return None


def _merge_all_of(schema: dict[str, Any]) -> dict[str, Any]:
    merged = {key: value for key, value in schema.items() if key != "allOf"}
    properties = dict(merged.get("properties") or {})
    required: list[str] = list(merged.get("required") or [])
    for item in schema.get("allOf") or []:
        if not isinstance(item, dict):
            continue
        properties.update(item.get("properties") or {})
        for required_field in item.get("required") or []:
            if required_field not in required:
                required.append(required_field)
        for key, value in item.items():
            if key not in {"properties", "required"}:
                merged.setdefault(key, value)
    if properties:
        merged["type"] = merged.get("type") or "object"
        merged["properties"] = properties
    if required:
        merged["required"] = required
    return merged


def _first_json_like_media(content: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(content, dict):
        return None
    for media_type in JSON_MEDIA_TYPES:
        if isinstance(content.get(media_type), dict):
            return content[media_type]
    for media in content.values():
        if isinstance(media, dict):
            return media
    return None


def _media_type(content: dict[str, Any], media: dict[str, Any]) -> str | None:
    for media_type, item in content.items():
        if item is media:
            return media_type
    return None


def _first_named_example(examples: Any) -> Any:
    if not isinstance(examples, dict) or not examples:
        return None
    example = next(iter(examples.values()))
    if isinstance(example, dict) and "value" in example:
        return example["value"]
    return example


def _preferred_response_status(responses: dict[str, Any]) -> str:
    for status_code in sorted(responses):
        if str(status_code).startswith("2"):
            return str(status_code)
    if responses:
        return str(next(iter(responses)))
    return "200"


def _first_defined(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None
