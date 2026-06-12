from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import api_endpoint_repository
from app.schemas.api_endpoint import ApiEndpointUpdate
from app.services.project_service import get_project


def list_api_endpoints(db: Session, project_id: int, skip: int = 0, limit: int = 20):
    get_project(db, project_id)
    return api_endpoint_repository.list_api_endpoints_by_project(db, project_id, skip=skip, limit=limit)


def get_api_endpoint(db: Session, endpoint_id: int):
    endpoint = api_endpoint_repository.get_api_endpoint(db, endpoint_id)
    if endpoint is None:
        raise HTTPException(status_code=404, detail="api endpoint not found")
    return endpoint


def update_api_endpoint(db: Session, endpoint_id: int, payload: ApiEndpointUpdate):
    endpoint = get_api_endpoint(db, endpoint_id)
    data = payload.model_dump(exclude_unset=True)
    return api_endpoint_repository.update_api_endpoint(db, endpoint, data)


def update_api_endpoint_status(db: Session, endpoint_id: int, status: str):
    endpoint = get_api_endpoint(db, endpoint_id)
    return api_endpoint_repository.update_api_endpoint(db, endpoint, {"status": status})
