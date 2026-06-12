from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.api_endpoint import ApiEndpoint


def create_api_endpoint(db: Session, data: dict) -> ApiEndpoint:
    endpoint = ApiEndpoint(**data)
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return endpoint


def create_api_endpoints(db: Session, items: list[dict]) -> list[ApiEndpoint]:
    endpoints = [ApiEndpoint(**item) for item in items]
    db.add_all(endpoints)
    db.commit()
    for endpoint in endpoints:
        db.refresh(endpoint)
    return endpoints


def list_api_endpoints_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 20) -> list[ApiEndpoint]:
    statement = (
        select(ApiEndpoint)
        .where(ApiEndpoint.project_id == project_id)
        .order_by(ApiEndpoint.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_api_endpoint(db: Session, endpoint_id: int) -> ApiEndpoint | None:
    return db.get(ApiEndpoint, endpoint_id)


def update_api_endpoint(db: Session, endpoint: ApiEndpoint, data: dict) -> ApiEndpoint:
    for key, value in data.items():
        setattr(endpoint, key, value)
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return endpoint
