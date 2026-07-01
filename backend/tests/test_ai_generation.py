from collections.abc import Generator
import json
from types import SimpleNamespace
from typing import Any

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


def create_endpoint(client: TestClient) -> tuple[dict[str, Any], dict[str, Any]]:
    project = client.post("/api/v1/projects", json={"name": "AI OpenAI Project"}).json()["data"]
    openapi_content = {
        "openapi": "3.0.0",
        "info": {"title": "Demo API", "version": "1.0.0"},
        "paths": {
            "/users/{id}": {
                "get": {
                    "tags": ["users"],
                    "summary": "Get user",
                    "parameters": [
                        {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}, "example": 1},
                        {"name": "verbose", "in": "query", "schema": {"type": "boolean"}, "example": True},
                    ],
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {"application/json": {"example": {"code": 200, "data": {"id": 1}}}},
                        }
                    },
                }
            }
        },
    }
    endpoint = client.post(
        f"/api/v1/projects/{project['id']}/api-documents/openapi",
        json={"name": "Demo OpenAPI", "content": openapi_content},
    ).json()["data"]["endpoints"][0]
    return project, endpoint


def valid_ai_payload() -> dict[str, Any]:
    return {
        "test_strategy": {
            "normal": [
                {
                    "name": "Get user normal",
                    "purpose": "Verify a valid user can be queried by id.",
                    "coverage_dimension": "functional",
                    "request": {"headers": {}, "query": {"verbose": True}, "path": {"id": 1}, "body": {}},
                    "assertions": ["status_code == 200", "$.code == 200", "$.data != null"],
                    "risk_level": "P1",
                    "reason": "This is the primary successful business path.",
                },
                {
                    "name": "Get user business semantic",
                    "purpose": "Verify the response business code and data semantics.",
                    "coverage_dimension": "business",
                    "request": {"headers": {}, "query": {"verbose": True}, "path": {"id": 1}, "body": {}},
                    "assertions": ["status_code == 200", "$.code == 200", "$.data != null"],
                    "risk_level": "P1",
                    "reason": "Business success can fail even when HTTP status is 200.",
                },
                {
                    "name": "Get user dependency data",
                    "purpose": "Verify the endpoint uses an existing user id dependency.",
                    "coverage_dimension": "dependency",
                    "request": {"headers": {}, "query": {}, "path": {"id": 1}, "body": {}},
                    "assertions": ["status_code == 200", "$.data != null"],
                    "risk_level": "P2",
                    "reason": "The path id depends on existing user data.",
                },
            ],
            "error": [
                {
                    "name": "Get user invalid id",
                    "purpose": "Verify invalid path id is rejected.",
                    "coverage_dimension": "validation",
                    "request": {"headers": {}, "query": {}, "path": {"id": ""}, "body": {}},
                    "assertions": ["status_code == 400"],
                    "risk_level": "P1",
                    "reason": "Path parameter validation is easy to break.",
                },
                {
                    "name": "Get user invalid query type",
                    "purpose": "Verify invalid query parameter type is rejected.",
                    "coverage_dimension": "validation",
                    "request": {"headers": {}, "query": {"verbose": "not_bool"}, "path": {"id": 1}, "body": {}},
                    "assertions": ["status_code == 400"],
                    "risk_level": "P1",
                    "reason": "Query parameter validation should reject wrong types.",
                },
                {
                    "name": "Get user not found",
                    "purpose": "Verify non-existing user id returns a controlled error.",
                    "coverage_dimension": "negative",
                    "request": {"headers": {}, "query": {}, "path": {"id": 999999}, "body": {}},
                    "assertions": ["status_code == 404"],
                    "risk_level": "P1",
                    "reason": "Not-found paths must not crash or return misleading success.",
                },
                {
                    "name": "Get user unsupported negative id",
                    "purpose": "Verify negative id is rejected.",
                    "coverage_dimension": "negative",
                    "request": {"headers": {}, "query": {}, "path": {"id": -1}, "body": {}},
                    "assertions": ["status_code == 400"],
                    "risk_level": "P1",
                    "reason": "Negative identifiers are a common invalid path.",
                },
            ],
            "boundary": [
                {
                    "name": "Get user zero id boundary",
                    "purpose": "Verify boundary id value is handled deterministically.",
                    "coverage_dimension": "boundary",
                    "request": {"headers": {}, "query": {"verbose": False}, "path": {"id": 0}, "body": {}},
                    "assertions": ["status_code == 200"],
                    "risk_level": "P2",
                    "reason": "Boundary values often expose validation gaps.",
                },
                {
                    "name": "Get user max id boundary",
                    "purpose": "Verify large id value is handled deterministically.",
                    "coverage_dimension": "boundary",
                    "request": {"headers": {}, "query": {"verbose": False}, "path": {"id": 2147483647}, "body": {}},
                    "assertions": ["status_code == 200"],
                    "risk_level": "P2",
                    "reason": "Maximum integer values can expose overflow or query issues.",
                },
            ],
            "security": [
                {
                    "name": "Get user unauthorized access",
                    "purpose": "Verify missing authorization cannot access protected data.",
                    "coverage_dimension": "security",
                    "request": {"headers": {}, "query": {"verbose": True}, "path": {"id": 1}, "body": {}},
                    "assertions": ["status_code == 401"],
                    "risk_level": "P0",
                    "reason": "Unauthorized access is a high-impact security risk.",
                }
            ],
        }
    }


def install_fake_openai(monkeypatch, payload: dict[str, Any] | str, captured: dict[str, Any]) -> None:
    class FakeCompletions:
        def create(self, **kwargs: Any) -> Any:
            captured["create_kwargs"] = kwargs
            content = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])

    class FakeOpenAI:
        def __init__(self, **kwargs: Any) -> None:
            captured["client_kwargs"] = kwargs
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr("app.ai.clients.openai_client.OpenAI", FakeOpenAI)


def install_fake_qwen(monkeypatch, payload: dict[str, Any] | str, captured: dict[str, Any]) -> None:
    class FakeCompletions:
        def create(self, **kwargs: Any) -> Any:
            captured["create_kwargs"] = kwargs
            content = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])

    class FakeOpenAI:
        def __init__(self, **kwargs: Any) -> None:
            captured["client_kwargs"] = kwargs
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr("app.ai.clients.qwen_client.OpenAI", FakeOpenAI)


def test_generate_real_ai_testcases_for_endpoint(monkeypatch) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr("app.ai.llm_factory.settings.ai_provider", "openai")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_api_base_url", "https://api.openai.com/v1")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_api_key", "sk-test")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_model_name", "gpt-4o-mini")
    install_fake_openai(monkeypatch, valid_ai_payload(), captured)

    client = build_client()
    project, endpoint = create_endpoint(client)

    response = client.post(f"/api/v1/endpoints/{endpoint['id']}/testcases/generate")

    assert captured["client_kwargs"]["base_url"] == "https://api.openai.com/v1"
    assert captured["client_kwargs"]["api_key"] == "sk-test"
    assert captured["create_kwargs"]["model"] == "gpt-4o-mini"
    assert captured["create_kwargs"]["response_format"] == {"type": "json_object"}
    assert "只返回严格 JSON" in captured["create_kwargs"]["messages"][0]["content"]
    user_prompt = json.loads(captured["create_kwargs"]["messages"][1]["content"])
    assert set(user_prompt["coverage"]["coverage_matrix"]) == {
        "functional",
        "validation",
        "boundary",
        "negative",
        "security",
        "business",
        "dependency",
    }
    assert all(user_prompt["coverage"]["coverage_matrix"].values())
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["endpoint_id"] == endpoint["id"]
    assert data["analysis_record_id"] > 0
    assert data["case_count"] == 10
    assert data["coverage_matrix"] == {
        "functional": True,
        "validation": True,
        "boundary": True,
        "negative": True,
        "security": True,
        "business": True,
        "dependency": True,
    }
    assert data["coverage_summary"]["missing_dimensions"] == []
    assert all(count > 0 for count in data["coverage_summary"]["counts"].values())
    assert {item["type"] for item in data["test_cases"]} == {
        "functional",
        "validation",
        "boundary",
        "negative",
        "security",
        "business",
        "dependency",
    }
    assert all(item["status"] == "generated" for item in data["test_cases"])
    assert all(item["priority"] in {"P0", "P1", "P2"} for item in data["test_cases"])
    assert all(item["endpoint"]["id"] == endpoint["id"] for item in data["test_cases"])
    assert all(item["assertions"] for item in data["test_cases"])
    assert all(item["dsl_assertions"] for item in data["test_cases"])
    assert all(item["coverage_tag"][0] == item["type"] for item in data["test_cases"])
    assert all(item["ai_metadata"]["source"] == "ai_openai" for item in data["test_cases"])
    assert all(item["ai_metadata"]["ai_provider"] == "openai" for item in data["test_cases"])
    assert all(item["ai_metadata"]["ai_generation_mode"] == "real_llm" for item in data["test_cases"])
    first_suggestions = data["test_cases"][0]["dsl_assertions"]
    assert first_suggestions == ["status_code == 200", "$.code == 200", "$.data != null"]
    assert "business_code == 1" not in json.dumps(data, ensure_ascii=False)

    list_response = client.get(f"/api/v1/projects/{project['id']}/test-cases")
    assert len(list_response.json()["data"]) == 10


def test_generate_qwen_testcases_without_response_format(monkeypatch) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr("app.ai.llm_factory.settings.ai_provider", "qwen")
    monkeypatch.setattr(
        "app.ai.clients.qwen_client.settings.ai_api_base_url",
        "https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    monkeypatch.setattr("app.ai.clients.qwen_client.settings.ai_api_key", "sk-qwen-test")
    monkeypatch.setattr("app.ai.clients.qwen_client.settings.ai_model_name", "qwen-max-latest")
    install_fake_qwen(monkeypatch, valid_ai_payload(), captured)

    client = build_client()
    project, endpoint = create_endpoint(client)

    response = client.post(f"/api/v1/endpoints/{endpoint['id']}/testcases/generate")

    assert captured["client_kwargs"]["base_url"] == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert captured["client_kwargs"]["api_key"] == "sk-qwen-test"
    assert captured["create_kwargs"]["model"] == "qwen-max-latest"
    assert "response_format" not in captured["create_kwargs"]
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["case_count"] == 10
    assert all(item["ai_metadata"]["source"] == "ai_qwen" for item in data["test_cases"])
    assert all(item["ai_metadata"]["ai_provider"] == "qwen" for item in data["test_cases"])
    assert all(isinstance(item["dsl_assertions"], list) for item in data["test_cases"])


def test_generate_testcases_requires_ai_configuration(monkeypatch) -> None:
    monkeypatch.setattr("app.ai.llm_factory.settings.ai_provider", "openai")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_api_base_url", "https://api.openai.com/v1")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_api_key", "")
    client = build_client()
    project, endpoint = create_endpoint(client)

    response = client.post(f"/api/v1/endpoints/{endpoint['id']}/testcases/generate")

    assert response.status_code == 400
    assert "AI_API_KEY 未配置，无法调用真实 OpenAI" in response.json()["message"]
    list_response = client.get(f"/api/v1/projects/{project['id']}/test-cases")
    assert list_response.json()["data"] == []


def test_generate_testcases_rejects_non_json_model_response(monkeypatch) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr("app.ai.llm_factory.settings.ai_provider", "openai")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_api_base_url", "https://api.openai.com/v1")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_api_key", "sk-test")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_model_name", "gpt-4o-mini")
    install_fake_openai(monkeypatch, "not json", captured)

    client = build_client()
    project, endpoint = create_endpoint(client)

    response = client.post(f"/api/v1/endpoints/{endpoint['id']}/testcases/generate")

    assert response.status_code == 502
    assert "不是有效 JSON" in response.json()["message"]
    list_response = client.get(f"/api/v1/projects/{project['id']}/test-cases")
    assert list_response.json()["data"] == []


def test_generate_testcases_rejects_legacy_object_assertions(monkeypatch) -> None:
    captured: dict[str, Any] = {}
    payload = valid_ai_payload()
    payload["test_strategy"]["normal"][0]["assertions"] = [{"type": "status_code", "expected": 200}]
    monkeypatch.setattr("app.ai.llm_factory.settings.ai_provider", "openai")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_api_base_url", "https://api.openai.com/v1")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_api_key", "sk-test")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_model_name", "gpt-4o-mini")
    install_fake_openai(monkeypatch, payload, captured)

    client = build_client()
    project, endpoint = create_endpoint(client)

    response = client.post(f"/api/v1/endpoints/{endpoint['id']}/testcases/generate")

    assert response.status_code == 502
    assert "DSL strings" in response.json()["message"]
    list_response = client.get(f"/api/v1/projects/{project['id']}/test-cases")
    assert list_response.json()["data"] == []


def test_generate_testcases_completes_missing_coverage_dimension(monkeypatch) -> None:
    captured: dict[str, Any] = {}
    payload = valid_ai_payload()
    payload["test_strategy"]["security"] = []
    monkeypatch.setattr("app.ai.llm_factory.settings.ai_provider", "openai")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_api_base_url", "https://api.openai.com/v1")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_api_key", "sk-test")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_model_name", "gpt-4o-mini")
    install_fake_openai(monkeypatch, payload, captured)

    client = build_client()
    project, endpoint = create_endpoint(client)

    response = client.post(f"/api/v1/endpoints/{endpoint['id']}/testcases/generate")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["coverage_summary"]["missing_dimensions"] == []
    assert data["coverage_summary"]["counts"]["security"] == 1
    assert any(
        item["type"] == "security"
        and item["ai_metadata"]["coverage_source"] == "coverage_engine"
        for item in data["test_cases"]
    )
    list_response = client.get(f"/api/v1/projects/{project['id']}/test-cases")
    assert len(list_response.json()["data"]) == 10


def test_generate_testcases_replaces_invalid_dsl_strings(monkeypatch) -> None:
    captured: dict[str, Any] = {}
    payload = valid_ai_payload()
    payload["test_strategy"]["normal"][0]["assertions"] = ["HTTP status should be 200"]
    monkeypatch.setattr("app.ai.llm_factory.settings.ai_provider", "openai")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_api_base_url", "https://api.openai.com/v1")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_api_key", "sk-test")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_model_name", "gpt-4o-mini")
    install_fake_openai(monkeypatch, payload, captured)

    client = build_client()
    _project, endpoint = create_endpoint(client)

    response = client.post(f"/api/v1/endpoints/{endpoint['id']}/testcases/generate")

    assert response.status_code == 200
    first_case = response.json()["data"]["test_cases"][0]
    assert first_case["dsl_assertions"] == ["status_code == 200", "$.data != null"]
