import json
import threading
from collections.abc import Generator
from http.server import BaseHTTPRequestHandler, HTTPServer

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


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = json.dumps({"code": 0, "data": {"id": 1}}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


class AuthDemoHandler(BaseHTTPRequestHandler):
    last_headers: dict[str, str] = {}

    def do_GET(self) -> None:
        AuthDemoHandler.last_headers = {key: value for key, value in self.headers.items()}
        body = json.dumps({"code": 200, "success": True, "data": {"id": 1}}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


class BusinessFailureHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = json.dumps({"code": 401, "msg": "invalid token", "data": None}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


class BusinessSuccessHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = json.dumps({"code": 200, "msg": "ok", "data": {"id": 1}}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


def start_demo_server() -> tuple[HTTPServer, str]:
    server = HTTPServer(("127.0.0.1", 0), DemoHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_port}"


def start_server(handler: type[BaseHTTPRequestHandler]) -> tuple[HTTPServer, str]:
    server = HTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_port}"


def test_run_execution_with_generated_pytest_project() -> None:
    server, base_url = start_demo_server()
    try:
        client = build_client()
        project = client.post("/api/v1/projects", json={"name": "Execution Project"}).json()["data"]
        environment = client.post(
            f"/api/v1/projects/{project['id']}/environments",
            json={"name": "local", "base_url": base_url, "is_default": True},
        ).json()["data"]
        test_case = client.post(
            "/api/v1/test-cases",
            json={
                "project_id": project["id"],
                "name": "GET demo",
                "status": "active",
                "steps": [
                    {
                        "name": "GET demo",
                        "request": {
                            "method": "GET",
                            "path": "/demo",
                            "headers": {},
                            "query": {},
                            "path_params": {},
                            "body": {},
                        },
                    }
                ],
                "assertions": [
                    {"type": "status_code", "expected": 200},
                    {"type": "json_path_equal", "path": "$.code", "expected": 0},
                    {"type": "json_path_not_null", "path": "$.data.id"},
                    {"type": "response_time", "expected": 3000},
                ],
            },
        ).json()["data"]

        response = client.post(
            "/api/v1/executions/run",
            json={
                "project_id": project["id"],
                "environment_id": environment["id"],
                "case_ids": [test_case["id"]],
                "timeout": 5,
            },
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["task"]["status"] == "passed"
        assert data["task"]["total_cases"] == 1
        assert data["task"]["passed_cases"] == 1
        assert data["pytest_exit_code"] == 0
        assert data["results"][0]["status"] == "passed"
        assert data["report"]["status"] == "created"
        assert data["generated_project_path"].startswith("storage/generated/")
        assert data["report_path"].startswith("storage/reports/")
        assert data["log_path"].startswith("storage/logs/")
    finally:
        server.shutdown()


def test_run_execution_merges_environment_auth_and_masks_sensitive_headers() -> None:
    server, base_url = start_server(AuthDemoHandler)
    try:
        client = build_client()
        project = client.post("/api/v1/projects", json={"name": "Auth Project"}).json()["data"]
        environment = client.post(
            f"/api/v1/projects/{project['id']}/environments",
            json={
                "name": "auth-env",
                "base_url": base_url,
                "headers": {"X-Env": "env-value"},
                "variables": {
                    "auth_type": "bearer",
                    "token": "stage10-secret-token",
                    "cookie": "SESSION=stage10-cookie",
                    "timeout_seconds": 5,
                    "retry_count": 1,
                },
            },
        ).json()["data"]
        test_case = client.post(
            "/api/v1/test-cases",
            json={
                "project_id": project["id"],
                "name": "GET auth demo",
                "status": "active",
                "steps": [{"name": "GET auth demo", "request": {"method": "GET", "path": "/auth"}}],
                "assertions": [
                    {"type": "status_code", "expected": 200},
                    {"type": "business_code", "path": "$.code", "expected": 200},
                    {"type": "business_success", "path": "$.success", "expected": True},
                    {"type": "json_path_not_empty", "path": "$.data"},
                ],
            },
        ).json()["data"]

        response = client.post(
            "/api/v1/executions/run",
            json={
                "project_id": project["id"],
                "environment_id": environment["id"],
                "case_ids": [test_case["id"]],
                "timeout": 5,
            },
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["task"]["status"] == "passed"
        assert AuthDemoHandler.last_headers["Authorization"] == "Bearer stage10-secret-token"
        assert AuthDemoHandler.last_headers["Cookie"] == "SESSION=stage10-cookie"
        assert AuthDemoHandler.last_headers["X-Env"] == "env-value"
        request_headers = data["results"][0]["request_data"]["headers"]
        assert request_headers["Authorization"] != "Bearer stage10-secret-token"
        assert request_headers["Cookie"] != "SESSION=stage10-cookie"
        assert "curl" in data["results"][0]["request_data"]
        assert "stage10-secret-token" not in data["results"][0]["request_data"]["curl"]
        assert "stage10-cookie" not in data["results"][0]["request_data"]["curl"]
    finally:
        server.shutdown()


def test_http_200_with_business_failure_is_failed() -> None:
    server, base_url = start_server(BusinessFailureHandler)
    try:
        client = build_client()
        project = client.post("/api/v1/projects", json={"name": "Business Assert Project"}).json()["data"]
        environment = client.post(
            f"/api/v1/projects/{project['id']}/environments",
            json={"name": "business-env", "base_url": base_url},
        ).json()["data"]
        endpoint = _import_business_endpoint(client, project["id"], "/business")
        test_case = client.post(
            "/api/v1/test-cases",
            json={
                "project_id": project["id"],
                "api_endpoint_id": endpoint["id"],
                "name": "GET business failure",
                "status": "active",
                "steps": [{"name": "GET business failure", "request": {"method": "GET", "path": "/business"}}],
                "assertions": [{"type": "status_code", "expected": 200}],
            },
        ).json()["data"]

        response = client.post(
            "/api/v1/executions/run",
            json={
                "project_id": project["id"],
                "environment_id": environment["id"],
                "case_ids": [test_case["id"]],
                "timeout": 5,
            },
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["task"]["status"] == "failed"
        assert data["task"]["failed_cases"] == 1
        assert data["results"][0]["status"] == "failed"
        assert data["results"][0]["status_code"] == 200
        assert "expected business code" in data["results"][0]["error_message"]
        messages = [item["message"] for item in data["results"][0]["assertion_result"]["items"]]
        assert any("skip data assertion because business failed" in message for message in messages)
    finally:
        server.shutdown()


def test_http_200_with_business_success_passes_swagger_assertions() -> None:
    server, base_url = start_server(BusinessSuccessHandler)
    try:
        client = build_client()
        project = client.post("/api/v1/projects", json={"name": "Business Success Project"}).json()["data"]
        environment = client.post(
            f"/api/v1/projects/{project['id']}/environments",
            json={"name": "business-env", "base_url": base_url},
        ).json()["data"]
        endpoint = _import_business_endpoint(client, project["id"], "/business-ok")
        test_case = client.post(
            "/api/v1/test-cases",
            json={
                "project_id": project["id"],
                "api_endpoint_id": endpoint["id"],
                "name": "GET business success",
                "status": "active",
                "steps": [{"name": "GET business success", "request": {"method": "GET", "path": "/business-ok"}}],
                "assertions": [{"type": "json_path_equal", "path": "$.code", "expected": 200}],
            },
        ).json()["data"]

        response = client.post(
            "/api/v1/executions/run",
            json={
                "project_id": project["id"],
                "environment_id": environment["id"],
                "case_ids": [test_case["id"]],
                "timeout": 5,
            },
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["task"]["status"] == "passed"
        assert data["results"][0]["assertion_result"]["passed"] is True
        sources = {item["assertion"]["source"] for item in data["results"][0]["assertion_result"]["items"]}
        assert "user" in sources
        assert "swagger" in sources
    finally:
        server.shutdown()


def _import_business_endpoint(client: TestClient, project_id: int, path: str) -> dict:
    openapi_content = {
        "openapi": "3.0.0",
        "info": {"title": "Business API", "version": "1.0.0"},
        "paths": {
            path: {
                "get": {
                    "summary": "Business endpoint",
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["code", "data"],
                                        "properties": {
                                            "code": {"type": "integer", "example": 200},
                                            "msg": {"type": "string"},
                                            "data": {
                                                "type": "object",
                                                "required": ["id"],
                                                "properties": {"id": {"type": "integer"}},
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            }
        },
    }
    response = client.post(
        f"/api/v1/projects/{project_id}/api-documents/openapi",
        json={"name": f"Business {path}", "content": openapi_content},
    )
    assert response.status_code == 200
    return response.json()["data"]["endpoints"][0]
