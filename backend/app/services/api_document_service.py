import json
from typing import Any

import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.parsers.curl_parser import parse_curl_text
from app.parsers.document_input_detector import detect_document_input_type, parse_method_path_hint
from app.parsers.endpoint_filter import build_endpoint_key, filter_endpoints
from app.parsers.html_ai_parser import mock_parse_html_document
from app.parsers.knife4j_resolver import resolve_openapi_from_url
from app.parsers.openapi_parser import parse_openapi_document
from app.parsers.swagger_parser import parse_swagger_document
from app.repositories import api_document_repository, api_endpoint_repository
from app.schemas.api_document import (
    CurlImportRequest,
    DocumentImportUrlRequest,
    DocumentPreviewRequest,
    DocumentPreviewResponse,
    EndpointPreviewItem,
    OpenApiImportRequest,
)
from app.services.project_service import get_project


def import_openapi_document(db: Session, project_id: int, payload: OpenApiImportRequest):
    get_project(db, project_id)
    raw_document = _load_openapi_payload(payload)
    parsed_data = _parse_openapi_or_swagger(raw_document)
    return _save_import_result(
        db=db,
        project_id=project_id,
        name=payload.name,
        source_type="openapi_url" if payload.url else "openapi_json",
        raw_content=json.dumps(raw_document, ensure_ascii=False),
        parsed_data=parsed_data,
    )


def import_openapi_file(db: Session, project_id: int, name: str, raw_bytes: bytes):
    get_project(db, project_id)
    try:
        raw_document = json.loads(raw_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=400, detail=f"invalid OpenAPI JSON file: {exc}") from exc
    parsed_data = _parse_openapi_or_swagger(raw_document)
    return _save_import_result(
        db=db,
        project_id=project_id,
        name=name,
        source_type="openapi_file",
        raw_content=json.dumps(raw_document, ensure_ascii=False),
        parsed_data=parsed_data,
    )


def import_curl(db: Session, project_id: int, payload: CurlImportRequest):
    get_project(db, project_id)
    try:
        parsed_data = parse_curl_text(payload.curl_text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _save_import_result(
        db=db,
        project_id=project_id,
        name=payload.name,
        source_type="curl",
        raw_content=payload.curl_text,
        parsed_data=parsed_data,
    )


def preview_document_input(db: Session, project_id: int, payload: DocumentPreviewRequest) -> DocumentPreviewResponse:
    get_project(db, project_id)
    preview = _build_preview(db, project_id, payload)
    return DocumentPreviewResponse(**preview)


def import_document_input(db: Session, project_id: int, payload: DocumentImportUrlRequest):
    get_project(db, project_id)
    preview = _build_preview(db, project_id, payload)
    endpoint_items = _select_preview_endpoints(payload, preview["endpoints"])
    if not endpoint_items:
        raise HTTPException(status_code=400, detail="no endpoints selected to save")

    parsed_data = {
        "version": "stage9-import",
        "title": payload.name,
        "endpoint_count": len(endpoint_items),
        "endpoints": [_preview_to_endpoint_dict(item) for item in endpoint_items],
        "stage9_meta": {
            "detected_type": preview["detected_type"],
            "resolved_spec_url": preview["resolved_spec_url"],
            "hash_hint": preview["hash_hint"],
            "total_endpoint_count": preview["total_endpoint_count"],
            "matched_endpoint_count": preview["matched_endpoint_count"],
            "save_mode": payload.save_mode,
            "warnings": preview["warnings"],
            "errors": preview["errors"],
            "filters": {
                "api_path_filter": payload.api_path_filter,
                "method_filter": payload.method_filter,
                "keyword_filter": payload.keyword_filter,
                "group_filter": payload.group_filter,
            },
        },
    }
    document = api_document_repository.create_api_document(
        db,
        {
            "project_id": project_id,
            "name": payload.name,
            "source_type": preview["detected_type"][:32],
            "raw_content": payload.input_content,
            "parsed_data": parsed_data,
            "status": "parsed",
        },
    )
    endpoints = api_endpoint_repository.create_api_endpoints(
        db,
        [_endpoint_to_model_data(project_id, document.id, _preview_to_endpoint_dict(item)) for item in endpoint_items],
    )
    return document, endpoints, preview


def _load_openapi_payload(payload: OpenApiImportRequest) -> dict[str, Any]:
    if payload.content is not None:
        return payload.content
    try:
        response = requests.get(str(payload.url), timeout=10)
        response.raise_for_status()
        return json.loads(response.content.decode("utf-8-sig"))
    except requests.RequestException as exc:
        raise HTTPException(status_code=400, detail=f"failed to fetch OpenAPI URL: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"OpenAPI URL did not return valid JSON: {exc}") from exc


def _parse_openapi_or_swagger(raw_document: dict[str, Any]) -> dict[str, Any]:
    try:
        if raw_document.get("swagger"):
            return parse_swagger_document(raw_document)
        return parse_openapi_document(raw_document)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _save_import_result(
    db: Session,
    project_id: int,
    name: str,
    source_type: str,
    raw_content: str,
    parsed_data: dict[str, Any],
):
    document = api_document_repository.create_api_document(
        db,
        {
            "project_id": project_id,
            "name": name,
            "source_type": source_type,
            "raw_content": raw_content,
            "parsed_data": parsed_data,
            "status": "parsed",
        },
    )
    endpoint_items = [_endpoint_to_model_data(project_id, document.id, item) for item in parsed_data["endpoints"]]
    endpoints = api_endpoint_repository.create_api_endpoints(db, endpoint_items)
    return document, endpoints


def _endpoint_to_model_data(project_id: int, document_id: int, endpoint: dict[str, Any]) -> dict[str, Any]:
    return {
        "project_id": project_id,
        "api_document_id": document_id,
        "name": endpoint["name"],
        "group_name": endpoint.get("group_name"),
        "method": endpoint["method"],
        "path": endpoint["path"],
        "description": endpoint.get("description"),
        "headers": endpoint.get("headers"),
        "request_params": endpoint.get("request_params"),
        "request_body_schema": endpoint.get("request_body_schema"),
        "response_schema": endpoint.get("response_schema"),
        "example_request": endpoint.get("example_request"),
        "example_response": endpoint.get("example_response"),
        "auth_required": endpoint.get("auth_required", False),
        "tags": endpoint.get("tags"),
        "status": endpoint.get("status", "active"),
    }


def _build_preview(db: Session, project_id: int, payload: DocumentPreviewRequest) -> dict[str, Any]:
    explicit_type = payload.input_type if payload.input_type != "auto" else None
    detected_type = explicit_type or detect_document_input_type(payload.input_content)
    errors: list[str] = []
    warnings: list[str] = []
    raw_document: dict[str, Any] | None = None
    parsed_data: dict[str, Any] | None = None
    resolved_spec_url: str | None = None
    hash_hint: str | None = None

    if detected_type == "openapi_json_text":
        try:
            raw_document = json.loads(payload.input_content)
        except json.JSONDecodeError as exc:
            errors.append(f"OpenAPI/Swagger JSON 内容格式错误: {exc}")
    elif detected_type in {"online_url", "single_api_doc_url", "openapi_json_url"}:
        resolved = resolve_openapi_from_url(payload.input_content, cookie=payload.cookie)
        raw_document = resolved.raw_document
        resolved_spec_url = resolved.resolved_spec_url
        hash_hint = resolved.hash_hint
        warnings.extend(resolved.warnings)
        errors.extend(resolved.errors)
        detected_type = resolved.detected_type if resolved.raw_document else detected_type
        if raw_document is None and payload.need_ai_parse:
            ai_result = mock_parse_html_document(url=payload.input_content, hash_hint=hash_hint)
            warnings.extend(ai_result.get("warnings", []))
    elif detected_type == "curl_text":
        try:
            parsed_data = parse_curl_text(payload.input_content)
        except ValueError as exc:
            errors.append(str(exc))
    elif detected_type == "api_path":
        return _build_api_path_preview(db, project_id, payload, detected_type)
    else:
        errors.append("无法识别输入内容，请提供 URL、OpenAPI/Swagger JSON、curl 文本或接口路径。")

    if raw_document is not None:
        try:
            parsed_data = _parse_openapi_or_swagger(raw_document)
        except HTTPException as exc:
            errors.append(str(exc.detail))

    endpoints = parsed_data.get("endpoints", []) if parsed_data else []
    method_hint, path_hint = parse_method_path_hint(payload.input_content)
    path_filter = payload.api_path_filter or path_hint
    method_filter = payload.method_filter or method_hint
    matched = filter_endpoints(
        [_normalize_endpoint_preview(item, source="parsed") for item in endpoints],
        path_filter=path_filter,
        method_filter=method_filter,
        keyword_filter=payload.keyword_filter,
        group_filter=payload.group_filter,
        hash_hint=hash_hint,
    )
    if endpoints and not matched:
        warnings.append("已解析文档，但没有匹配当前筛选条件的接口。")
    return {
        "detected_type": detected_type,
        "resolved_spec_url": resolved_spec_url,
        "hash_hint": hash_hint,
        "total_endpoint_count": len(endpoints),
        "matched_endpoint_count": len(matched),
        "endpoints": matched,
        "warnings": warnings,
        "errors": errors,
    }


def _build_api_path_preview(
    db: Session,
    project_id: int,
    payload: DocumentPreviewRequest,
    detected_type: str,
) -> dict[str, Any]:
    method_hint, path_hint = parse_method_path_hint(payload.input_content)
    path_filter = payload.api_path_filter or path_hint
    method_filter = payload.method_filter or method_hint
    warnings: list[str] = []
    endpoints = [
        _endpoint_model_to_preview(endpoint)
        for endpoint in api_endpoint_repository.list_api_endpoints_by_project(db, project_id, skip=0, limit=1000)
    ]
    matched = filter_endpoints(
        endpoints,
        path_filter=path_filter,
        method_filter=method_filter,
        keyword_filter=payload.keyword_filter,
        group_filter=payload.group_filter,
    )
    if not matched and path_filter:
        draft_method = (method_filter or "GET").upper()
        matched = [
            _normalize_endpoint_preview(
                {
                    "name": f"{draft_method} {path_filter}",
                    "group_name": "manual-draft",
                    "method": draft_method,
                    "path": path_filter,
                    "description": "接口路径草稿，仅保存基础信息，请手动补充参数结构。",
                    "headers": None,
                    "request_params": {"query": {}, "path": {}},
                    "request_body_schema": None,
                    "response_schema": None,
                    "example_request": {"method": draft_method, "path": path_filter},
                    "example_response": None,
                    "auth_required": False,
                    "tags": ["manual-draft"],
                    "status": "draft",
                },
                source="draft",
            )
        ]
        warnings.append("未在已有接口资产中找到该路径，仅生成待完善接口草稿，不会凭空补全参数。")
    return {
        "detected_type": detected_type,
        "resolved_spec_url": None,
        "hash_hint": None,
        "total_endpoint_count": len(endpoints),
        "matched_endpoint_count": len(matched),
        "endpoints": matched,
        "warnings": warnings,
        "errors": [],
    }


def _select_preview_endpoints(payload: DocumentImportUrlRequest, preview_endpoints: list[dict[str, Any]]) -> list[EndpointPreviewItem]:
    source_items = payload.endpoints if payload.endpoints is not None else [
        EndpointPreviewItem.model_validate(item) for item in preview_endpoints
    ]
    if payload.save_mode == "save_all":
        return list(source_items)
    selected = set(payload.selected_endpoint_keys)
    return [item for item in source_items if item.endpoint_key in selected]


def _normalize_endpoint_preview(endpoint: dict[str, Any], source: str) -> dict[str, Any]:
    normalized = {
        "name": endpoint.get("name") or f"{endpoint.get('method', 'GET')} {endpoint.get('path', '/')}",
        "group_name": endpoint.get("group_name"),
        "summary": endpoint.get("summary"),
        "operation_id": endpoint.get("operation_id"),
        "method": str(endpoint.get("method") or "GET").upper(),
        "path": endpoint.get("path") or "/",
        "description": endpoint.get("description"),
        "headers": endpoint.get("headers"),
        "request_params": endpoint.get("request_params"),
        "request_body_schema": endpoint.get("request_body_schema"),
        "response_schema": endpoint.get("response_schema"),
        "example_request": endpoint.get("example_request"),
        "example_response": endpoint.get("example_response"),
        "auth_required": bool(endpoint.get("auth_required", False)),
        "tags": endpoint.get("tags"),
        "status": endpoint.get("status") or "active",
        "source": source,
    }
    normalized["endpoint_key"] = build_endpoint_key(normalized)
    return normalized


def _endpoint_model_to_preview(endpoint) -> dict[str, Any]:
    return _normalize_endpoint_preview(
        {
            "name": endpoint.name,
            "group_name": endpoint.group_name,
            "method": endpoint.method,
            "path": endpoint.path,
            "description": endpoint.description,
            "headers": endpoint.headers,
            "request_params": endpoint.request_params,
            "request_body_schema": endpoint.request_body_schema,
            "response_schema": endpoint.response_schema,
            "example_request": endpoint.example_request,
            "example_response": endpoint.example_response,
            "auth_required": endpoint.auth_required,
            "tags": endpoint.tags,
            "status": endpoint.status,
        },
        source="existing_asset",
    )


def _preview_to_endpoint_dict(item: EndpointPreviewItem) -> dict[str, Any]:
    data = item.model_dump()
    data.pop("endpoint_key", None)
    data.pop("source", None)
    data.pop("summary", None)
    data.pop("operation_id", None)
    return data
