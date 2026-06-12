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


def test_import_openapi_json_content() -> None:
    client = build_client()
    project = client.post("/api/v1/projects", json={"name": "Import Project"}).json()["data"]

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
                        {"name": "X-Trace-Id", "in": "header", "schema": {"type": "string"}, "example": "trace-1"},
                    ],
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"id": {"type": "integer"}}},
                                    "example": {"id": 1},
                                }
                            },
                        }
                    },
                }
            }
        },
    }

    response = client.post(
        f"/api/v1/projects/{project['id']}/api-documents/openapi",
        json={"name": "Demo OpenAPI", "content": openapi_content},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["endpoint_count"] == 1
    endpoint = data["endpoints"][0]
    assert endpoint["name"] == "Get user"
    assert endpoint["group_name"] == "users"
    assert endpoint["method"] == "GET"
    assert endpoint["path"] == "/users/{id}"
    assert endpoint["headers"]["X-Trace-Id"]["example"] == "trace-1"
    assert endpoint["request_params"]["path"]["id"]["required"] is True
    assert endpoint["response_schema"]["type"] == "object"
    assert endpoint["example_response"] == {"id": 1}
    assert endpoint["auth_required"] is True

    list_response = client.get(f"/api/v1/projects/{project['id']}/api-endpoints")
    assert list_response.json()["data"][0]["api_document_id"] == data["document"]["id"]


def test_import_curl_text() -> None:
    client = build_client()
    project = client.post("/api/v1/projects", json={"name": "Curl Project"}).json()["data"]
    curl_text = (
        "curl -X POST 'https://api.example.com/users?debug=true' "
        "-H 'Authorization: Bearer token' -H 'Content-Type: application/json' "
        "--data-raw '{\"name\":\"Alice\"}'"
    )

    response = client.post(
        f"/api/v1/projects/{project['id']}/api-documents/curl",
        json={"name": "Create user curl", "curl_text": curl_text},
    )

    assert response.status_code == 200
    endpoint = response.json()["data"]["endpoints"][0]
    assert endpoint["group_name"] == "curl"
    assert endpoint["method"] == "POST"
    assert endpoint["path"] == "/users"
    assert endpoint["headers"]["Authorization"] == "Bearer token"
    assert endpoint["request_params"]["query"]["debug"] == "true"
    assert endpoint["request_body_schema"]["raw"] == '{"name":"Alice"}'
    assert endpoint["auth_required"] is True
