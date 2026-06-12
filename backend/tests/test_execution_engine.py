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


def start_demo_server() -> tuple[HTTPServer, str]:
    server = HTTPServer(("127.0.0.1", 0), DemoHandler)
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
