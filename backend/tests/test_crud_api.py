from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models.api_endpoint import ApiEndpoint


def build_client() -> tuple[TestClient, sessionmaker[Session]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), TestingSessionLocal


def test_project_and_environment_crud() -> None:
    client, _ = build_client()

    create_project_response = client.post(
        "/api/v1/projects",
        json={"name": "Demo Project", "description": "first project", "owner_name": "tester"},
    )
    assert create_project_response.status_code == 200
    project = create_project_response.json()["data"]
    assert project["name"] == "Demo Project"

    project_id = project["id"]
    assert client.get("/api/v1/projects").json()["data"][0]["id"] == project_id
    assert client.get(f"/api/v1/projects/{project_id}").json()["data"]["name"] == "Demo Project"

    update_project_response = client.put(f"/api/v1/projects/{project_id}", json={"name": "Updated Project"})
    assert update_project_response.json()["data"]["name"] == "Updated Project"

    create_environment_response = client.post(
        f"/api/v1/projects/{project_id}/environments",
        json={
            "name": "test",
            "base_url": "https://api.example.com",
            "variables": {"token": "mock"},
            "headers": {"X-Env": "test"},
            "is_default": True,
        },
    )
    assert create_environment_response.status_code == 200
    environment = create_environment_response.json()["data"]
    assert environment["project_id"] == project_id

    environment_id = environment["id"]
    assert client.get(f"/api/v1/projects/{project_id}/environments").json()["data"][0]["id"] == environment_id

    update_environment_response = client.put(
        f"/api/v1/environments/{environment_id}",
        json={"base_url": "https://new.example.com"},
    )
    assert update_environment_response.json()["data"]["base_url"] == "https://new.example.com"

    disable_environment_response = client.delete(f"/api/v1/environments/{environment_id}")
    assert disable_environment_response.json()["data"]["status"] == "inactive"

    disable_project_response = client.delete(f"/api/v1/projects/{project_id}")
    assert disable_project_response.json()["data"]["status"] == "inactive"


def test_api_endpoint_and_test_case_crud() -> None:
    client, SessionLocal = build_client()

    project = client.post("/api/v1/projects", json={"name": "API Project"}).json()["data"]
    project_id = project["id"]

    with SessionLocal() as db:
        endpoint = ApiEndpoint(
            project_id=project_id,
            name="Get User",
            method="GET",
            path="/users/{id}",
            description="get user by id",
            status="active",
        )
        db.add(endpoint)
        db.commit()
        db.refresh(endpoint)
        endpoint_id = endpoint.id

    endpoint_list = client.get(f"/api/v1/projects/{project_id}/api-endpoints").json()["data"]
    assert endpoint_list[0]["id"] == endpoint_id

    endpoint_detail = client.get(f"/api/v1/api-endpoints/{endpoint_id}").json()["data"]
    assert endpoint_detail["name"] == "Get User"

    update_endpoint_response = client.put(
        f"/api/v1/api-endpoints/{endpoint_id}",
        json={"name": "Get User Detail", "method": "post"},
    )
    assert update_endpoint_response.json()["data"]["method"] == "POST"

    disable_endpoint_response = client.patch(
        f"/api/v1/api-endpoints/{endpoint_id}/status",
        json={"status": "inactive"},
    )
    assert disable_endpoint_response.json()["data"]["status"] == "inactive"

    create_case_response = client.post(
        "/api/v1/test-cases",
        json={
            "project_id": project_id,
            "api_endpoint_id": endpoint_id,
            "name": "Get user success",
            "steps": [{"name": "request user"}],
            "assertions": [{"type": "status_code", "expected": 200}],
        },
    )
    assert create_case_response.status_code == 200
    test_case = create_case_response.json()["data"]
    assert test_case["project_id"] == project_id

    test_case_id = test_case["id"]
    assert client.get(f"/api/v1/projects/{project_id}/test-cases").json()["data"][0]["id"] == test_case_id
    assert client.get(f"/api/v1/test-cases/{test_case_id}").json()["data"]["name"] == "Get user success"

    update_case_response = client.put(
        f"/api/v1/test-cases/{test_case_id}",
        json={"priority": "high", "status": "active"},
    )
    assert update_case_response.json()["data"]["priority"] == "P0"

    disable_case_response = client.delete(f"/api/v1/test-cases/{test_case_id}")
    assert disable_case_response.json()["data"]["status"] == "disabled"
