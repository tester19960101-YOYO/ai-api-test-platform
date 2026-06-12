from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.db.session import get_db
from app.schemas.api_document import ApiDocumentImportResult, ApiDocumentRead, CurlImportRequest, OpenApiImportRequest
from app.schemas.api_endpoint import ApiEndpointRead
from app.services import api_document_service

router = APIRouter()


@router.post("/projects/{project_id}/api-documents/openapi")
def import_openapi_document(project_id: int, payload: OpenApiImportRequest, db: Session = Depends(get_db)) -> dict:
    document, endpoints = api_document_service.import_openapi_document(db, project_id, payload)
    return success_response(_build_import_result(document, endpoints))


@router.post("/projects/{project_id}/api-documents/openapi-file")
async def import_openapi_file(
    project_id: int,
    file: UploadFile = File(...),
    name: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> dict:
    raw_bytes = await file.read()
    document_name = name or file.filename or "OpenAPI Document"
    document, endpoints = api_document_service.import_openapi_file(db, project_id, document_name, raw_bytes)
    return success_response(_build_import_result(document, endpoints))


@router.post("/projects/{project_id}/api-documents/curl")
def import_curl(project_id: int, payload: CurlImportRequest, db: Session = Depends(get_db)) -> dict:
    document, endpoints = api_document_service.import_curl(db, project_id, payload)
    return success_response(_build_import_result(document, endpoints))


def _build_import_result(document, endpoints) -> ApiDocumentImportResult:
    endpoint_reads = [ApiEndpointRead.model_validate(endpoint) for endpoint in endpoints]
    return ApiDocumentImportResult(
        document=ApiDocumentRead.model_validate(document),
        endpoints=endpoint_reads,
        endpoint_count=len(endpoint_reads),
    )
