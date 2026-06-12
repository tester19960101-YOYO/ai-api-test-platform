from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.response import success_response
from app.db.session import get_db
from app.schemas.api_endpoint import ApiEndpointRead, ApiEndpointUpdate
from app.schemas.common import StatusUpdate
from app.services import api_endpoint_service

router = APIRouter()


@router.get("/projects/{project_id}/api-endpoints")
def list_api_endpoints(
    project_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    endpoints = api_endpoint_service.list_api_endpoints(db, project_id, skip=skip, limit=limit)
    return success_response([ApiEndpointRead.model_validate(endpoint) for endpoint in endpoints])


@router.get("/api-endpoints/{endpoint_id}")
def get_api_endpoint(endpoint_id: int, db: Session = Depends(get_db)) -> dict:
    endpoint = api_endpoint_service.get_api_endpoint(db, endpoint_id)
    return success_response(ApiEndpointRead.model_validate(endpoint))


@router.put("/api-endpoints/{endpoint_id}")
def update_api_endpoint(endpoint_id: int, payload: ApiEndpointUpdate, db: Session = Depends(get_db)) -> dict:
    endpoint = api_endpoint_service.update_api_endpoint(db, endpoint_id, payload)
    return success_response(ApiEndpointRead.model_validate(endpoint))


@router.patch("/api-endpoints/{endpoint_id}/status")
def update_api_endpoint_status(endpoint_id: int, payload: StatusUpdate, db: Session = Depends(get_db)) -> dict:
    endpoint = api_endpoint_service.update_api_endpoint_status(db, endpoint_id, payload.status)
    return success_response(ApiEndpointRead.model_validate(endpoint))
