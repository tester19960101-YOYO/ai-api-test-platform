import json
from typing import Any

import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.parsers.curl_parser import parse_curl_text
from app.parsers.openapi_parser import parse_openapi_document
from app.parsers.swagger_parser import parse_swagger_document
from app.repositories import api_document_repository, api_endpoint_repository
from app.schemas.api_document import CurlImportRequest, OpenApiImportRequest
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
        "status": "active",
    }
