from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app


def build_client() -> TestClient:
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
    return TestClient(app)


def test_generate_mock_testcases_for_endpoint() -> None:
    client = build_client()
    project = client.post("/api/v1/projects", json={"name": "AI Mock Project"}).json()["data"]
    openapi_content = {
        "openapi": "3.0.0",
        "info": {"title": "Demo API", "version": "1.0.0"},
        "security": [{"bearerAuth": []}],
        "paths": {
            "/users/{id}": {
                "get": {
                    "tags": ["users"],
                    "summary": "Get user",
                    "parameters": [
                        {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}, "example": 1},
                        {"name": "verbose", "in": "query", "schema": {"type": "boolean"}, "example": True},
                        {"name": "Authorization", "in": "header", "schema": {"type": "string"}, "example": "Bearer token"},
                    ],
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"id": {"type": "integer"}}},
                                    "example": {"id": 1, "name": "Alice"},
                                }
                            },
                        }
                    },
                }
            }
        },
    }
    import_response = client.post(
        f"/api/v1/projects/{project['id']}/api-documents/openapi",
        json={"name": "Demo OpenAPI", "content": openapi_content},
    )
    endpoint = import_response.json()["data"]["endpoints"][0]

    response = client.post(f"/api/v1/endpoints/{endpoint['id']}/testcases/generate")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["endpoint_id"] == endpoint["id"]
    assert data["analysis_record_id"] > 0
    assert data["case_count"] == 4
    assert {item["variables"]["case_type"] for item in data["test_cases"]} == {
        "normal",
        "exception",
        "boundary",
        "auth",
    }
    assert all(item["status"] == "generated" for item in data["test_cases"])
    assert all(item["assertions"] == [] for item in data["test_cases"])
    assert all("ai_assertion_dsl" in item["variables"] for item in data["test_cases"])
    first_suggestions = data["test_cases"][0]["variables"]["ai_assertion_dsl"]
    assert all(isinstance(item, str) for item in first_suggestions)
    assert "status_code == 200" in first_suggestions

    list_response = client.get(f"/api/v1/projects/{project['id']}/test-cases")
    assert len(list_response.json()["data"]) == 4
