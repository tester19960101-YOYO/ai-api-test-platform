from collections.abc import Generator
import json
from types import SimpleNamespace

from fastapi.testclient import TestClient
import requests
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


def test_preview_openapi_json_text_and_save_selected() -> None:
    client = build_client()
    project = client.post("/api/v1/projects", json={"name": "Preview Project"}).json()["data"]
    openapi_content = {
        "openapi": "3.0.0",
        "info": {"title": "Stage9 API", "version": "1.0.0"},
        "paths": {
            "/rainfall/add": {
                "post": {
                    "tags": ["rainfall"],
                    "summary": "鏂板闆ㄩ噺",
                    "operationId": "addRainfall",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"type": "object", "properties": {"amount": {"type": "number"}}}
                            }
                        }
                    },
                    "responses": {"200": {"description": "ok"}},
                }
            },
            "/rainfall/list": {
                "get": {
                    "tags": ["rainfall"],
                    "summary": "闆ㄩ噺鍒楄〃",
                    "responses": {"200": {"description": "ok"}},
                }
            },
        },
    }

    preview = client.post(
        f"/api/v1/projects/{project['id']}/documents/preview-url",
        json={
            "name": "Stage9 Preview",
            "input_type": "openapi_json_text",
            "input_content": json.dumps(openapi_content, ensure_ascii=False),
            "api_path_filter": "/rainfall/add",
            "method_filter": "POST",
            "need_ai_parse": True,
        },
    )

    assert preview.status_code == 200
    preview_data = preview.json()["data"]
    assert preview_data["total_endpoint_count"] == 2
    assert preview_data["matched_endpoint_count"] == 1
    assert preview_data["endpoints"][0]["operation_id"] == "addRainfall"

    saved = client.post(
        f"/api/v1/projects/{project['id']}/documents/import-url",
        json={
            "name": "Stage9 Save",
            "input_type": "openapi_json_text",
            "input_content": json.dumps(openapi_content, ensure_ascii=False),
            "api_path_filter": "/rainfall/add",
            "method_filter": "POST",
            "need_ai_parse": True,
            "save_mode": "save_selected",
            "selected_endpoint_keys": [preview_data["endpoints"][0]["endpoint_key"]],
            "endpoints": preview_data["endpoints"],
        },
    )

    assert saved.status_code == 200
    saved_data = saved.json()["data"]
    assert saved_data["endpoint_count"] == 1
    assert saved_data["endpoints"][0]["path"] == "/rainfall/add"


def test_openapi_ref_expansion_examples_and_ai_generation(monkeypatch) -> None:
    captured: dict = {}
    ai_payload = {
        "test_strategy": {
            "normal": [
                    {
                        "name": "create device normal",
                        "purpose": "Verify a valid device can be created.",
                        "coverage_dimension": "functional",
                        "request": {
                            "headers": {},
                            "query": {"debug": False},
                        "path": {"id": "1001"},
                        "body": {"name": "雨量监测仪", "params": {"threshold": 10}, "tags": ["rain"]},
                    },
                    "assertions": ["status_code == 200", "$.code == 200"],
                        "risk_level": "P1",
                        "reason": "Device creation is the primary business path.",
                    },
                    {
                        "name": "create device business semantic",
                        "purpose": "Verify business response fields indicate success.",
                        "coverage_dimension": "business",
                        "request": {
                            "headers": {},
                            "query": {"debug": False},
                            "path": {"id": "1001"},
                            "body": {"name": "雨量监测仪", "params": {"threshold": 10}, "tags": ["rain"]},
                        },
                        "assertions": ["status_code == 200", "$.code == 200", "$.data != null"],
                        "risk_level": "P1",
                        "reason": "Business response may fail while HTTP remains successful.",
                    },
                    {
                        "name": "create device dependency",
                        "purpose": "Verify creation with required upstream identifier.",
                        "coverage_dimension": "dependency",
                        "request": {
                            "headers": {},
                            "query": {"debug": False},
                            "path": {"id": "1001"},
                            "body": {"name": "雨量监测仪", "params": {"threshold": 10}, "tags": ["rain"]},
                        },
                        "assertions": ["status_code == 200"],
                        "risk_level": "P2",
                        "reason": "The API depends on a valid path id and request body data.",
                    }
                ],
                "error": [
                    {
                        "name": "create device missing id",
                        "purpose": "Verify missing path id is rejected.",
                        "coverage_dimension": "validation",
                        "request": {"headers": {}, "query": {}, "path": {"id": ""}, "body": {}},
                        "assertions": ["status_code == 400"],
                        "risk_level": "P1",
                        "reason": "Required path parameter validation must be covered.",
                    },
                    {
                        "name": "create device missing name",
                        "purpose": "Verify required body name is rejected.",
                        "coverage_dimension": "validation",
                        "request": {
                            "headers": {},
                            "query": {"debug": False},
                            "path": {"id": "1001"},
                            "body": {"params": {"threshold": 10}, "tags": ["rain"]},
                        },
                        "assertions": ["status_code == 400"],
                        "risk_level": "P1",
                        "reason": "Required body field validation must be covered.",
                    },
                    {
                        "name": "create device malformed body",
                        "purpose": "Verify malformed body is rejected.",
                        "coverage_dimension": "negative",
                        "request": {
                            "headers": {},
                            "query": {"debug": False},
                            "path": {"id": "1001"},
                            "body": {"name": "", "params": {}, "tags": []},
                        },
                        "assertions": ["status_code == 400"],
                        "risk_level": "P1",
                        "reason": "Negative request body should not create invalid devices.",
                    },
                    {
                        "name": "create device invalid id",
                        "purpose": "Verify invalid path id is rejected.",
                        "coverage_dimension": "negative",
                        "request": {
                            "headers": {},
                            "query": {"debug": False},
                            "path": {"id": "../admin"},
                            "body": {"name": "雨量监测仪", "params": {"threshold": 10}, "tags": ["rain"]},
                        },
                        "assertions": ["status_code == 400"],
                        "risk_level": "P1",
                        "reason": "Invalid path values should be rejected safely.",
                    }
                ],
                "boundary": [
                    {
                        "name": "create device threshold zero",
                        "purpose": "Verify boundary threshold value is handled.",
                        "coverage_dimension": "boundary",
                        "request": {
                            "headers": {},
                            "query": {"debug": False},
                        "path": {"id": "0"},
                        "body": {"name": "雨量监测仪", "params": {"threshold": 0}, "tags": ["rain"]},
                    },
                        "assertions": ["status_code == 200"],
                        "risk_level": "P2",
                        "reason": "Numeric boundary values often cause business defects.",
                    },
                    {
                        "name": "create device threshold max",
                        "purpose": "Verify maximum threshold value is handled.",
                        "coverage_dimension": "boundary",
                        "request": {
                            "headers": {},
                            "query": {"debug": False},
                            "path": {"id": "1001"},
                            "body": {"name": "雨量监测仪", "params": {"threshold": 2147483647}, "tags": ["rain"]},
                        },
                        "assertions": ["status_code == 200"],
                        "risk_level": "P2",
                        "reason": "Large numeric values can expose overflow or range defects.",
                    }
                ],
                "security": [
                    {
                        "name": "create device without auth",
                        "purpose": "Verify unauthorized request is rejected.",
                        "coverage_dimension": "security",
                        "request": {
                            "headers": {},
                            "query": {"debug": False},
                        "path": {"id": "1001"},
                        "body": {"name": "雨量监测仪", "params": {"threshold": 10}, "tags": ["rain"]},
                    },
                    "assertions": ["status_code == 401"],
                    "risk_level": "P0",
                    "reason": "Unauthorized creation can cause high-impact data risk.",
                }
            ],
        }
    }

    class FakeCompletions:
        def create(self, **kwargs: object) -> object:
            captured["create_kwargs"] = kwargs
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content=json.dumps(ai_payload, ensure_ascii=False))
                    )
                ]
            )

    class FakeOpenAI:
        def __init__(self, **kwargs: object) -> None:
            captured["client_kwargs"] = kwargs
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr("app.ai.llm_factory.settings.ai_provider", "openai")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_api_base_url", "https://api.openai.com/v1")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_api_key", "sk-test")
    monkeypatch.setattr("app.ai.clients.openai_client.settings.ai_model_name", "gpt-4o-mini")
    monkeypatch.setattr("app.ai.clients.openai_client.OpenAI", FakeOpenAI)

    client = build_client()
    project = client.post("/api/v1/projects", json={"name": "Ref Project"}).json()["data"]
    openapi_content = {
        "openapi": "3.0.0",
        "info": {"title": "Ref API", "version": "1.0.0"},
        "paths": {
            "/devices/{id}": {
                "post": {
                    "tags": ["device"],
                    "summary": "鍒涘缓璁惧",
                    "operationId": "createDevice",
                    "parameters": [
                        {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}, "example": "1001"},
                        {"name": "debug", "in": "query", "schema": {"type": "boolean"}, "default": False},
                        {"name": "X-Tenant", "in": "header", "schema": {"type": "string"}, "example": "tenant-a"},
                        {"name": "SESSION", "in": "cookie", "schema": {"type": "string"}, "example": "cookie-value"},
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/DeviceCreate"}
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CommonResultDevice"}
                                }
                            },
                        }
                    },
                }
            }
        },
        "components": {
            "schemas": {
                "DeviceCreate": {
                    "type": "object",
                    "required": ["name", "params"],
                    "properties": {
                        "name": {"type": "string", "example": "雨量监测仪"},
                        "ctime": {"type": "string", "default": "2024-12-01 00:00:00"},
                        "params": {
                            "type": "object",
                            "properties": {"threshold": {"type": "integer", "default": 10}},
                        },
                        "tags": {"type": "array", "items": {"type": "string", "example": "rain"}},
                    },
                },
                "CommonResultDevice": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "integer", "example": 200},
                        "msg": {"type": "string", "example": "操作成功"},
                        "data": {"$ref": "#/components/schemas/DeviceCreate"},
                    },
                },
            }
        },
    }

    preview = client.post(
        f"/api/v1/projects/{project['id']}/documents/preview-url",
        json={
            "name": "Ref Preview",
            "input_type": "openapi_json_text",
            "input_content": json.dumps(openapi_content, ensure_ascii=False),
            "method_filter": "POST",
            "api_path_filter": "/devices/{id}",
            "need_ai_parse": True,
        },
    )

    assert preview.status_code == 200
    endpoint = preview.json()["data"]["endpoints"][0]
    assert endpoint["request_params"]["query"]["debug"]["value"] is False
    assert endpoint["request_params"]["path"]["id"]["value"] == "1001"
    assert endpoint["request_params"]["header"]["X-Tenant"]["value"] == "tenant-a"
    assert endpoint["request_params"]["cookie"]["SESSION"]["value"] == "cookie-value"
    assert endpoint["example_request"]["body"]["name"] == "雨量监测仪"
    assert endpoint["example_request"]["body"]["params"]["threshold"] == 10
    assert endpoint["example_request"]["body"]["tags"] == ["rain"]
    assert endpoint["request_body_schema"]["properties"]["params"]["type"] == "object"
    assert endpoint["response_schema"]["properties"]["data"]["properties"]["name"]["example"] == "雨量监测仪"
    assert endpoint["example_response"]["data"]["params"]["threshold"] == 10

    saved = client.post(
        f"/api/v1/projects/{project['id']}/documents/import-url",
        json={
            "name": "Ref Save",
            "input_type": "openapi_json_text",
            "input_content": json.dumps(openapi_content, ensure_ascii=False),
            "method_filter": "POST",
            "api_path_filter": "/devices/{id}",
            "need_ai_parse": True,
            "save_mode": "save_all",
            "selected_endpoint_keys": [],
            "endpoints": [endpoint],
        },
    )

    assert saved.status_code == 200
    saved_endpoint = saved.json()["data"]["endpoints"][0]
    assert saved_endpoint["example_request"]["body"]["name"] == "雨量监测仪"
    ai_response = client.post(f"/api/v1/endpoints/{saved_endpoint['id']}/testcases/generate")
    assert ai_response.status_code == 200
    generated_case = ai_response.json()["data"]["test_cases"][0]
    assert generated_case["request"]["body"]["name"] == "雨量监测仪"
    assert generated_case["endpoint"]["id"] == saved_endpoint["id"]
    assert generated_case["dsl_assertions"]


def test_preview_doc_html_url_auto_discovers_openapi(monkeypatch) -> None:
    client = build_client()
    project = client.post("/api/v1/projects", json={"name": "Knife4j Project"}).json()["data"]
    openapi_content = {
        "openapi": "3.0.0",
        "info": {"title": "Knife4j Demo", "version": "1.0.0"},
        "paths": {
            "/saw/rainfallmonitor/add": {
                "post": {
                    "tags": ["yingji"],
                    "summary": "鏂板闆ㄩ噺鐩戞祴",
                    "operationId": "addRainfallMonitor",
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    class FakeResponse:
        def __init__(self, payload: object, status_code: int = 200) -> None:
            self.status_code = status_code
            self.content = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise requests.HTTPError("not found")

    def fake_get(url: str, **_: object) -> FakeResponse:
        if url.endswith("/v3/api-docs"):
            return FakeResponse(openapi_content)
        return FakeResponse("<html></html>")

    monkeypatch.setattr(requests, "get", fake_get)
    response = client.post(
        f"/api/v1/projects/{project['id']}/documents/preview-url",
        json={
            "name": "Knife4j Preview",
            "input_type": "auto",
            "input_content": "http://example.test/doc.html#/yingji/闆ㄩ噺鐩戞祴鎺у埗鍣?add_13",
            "api_path_filter": "/saw/rainfallmonitor/add",
            "method_filter": "POST",
            "need_ai_parse": True,
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["resolved_spec_url"] == "http://example.test/v3/api-docs"
    assert data["hash_hint"] == "/yingji/闆ㄩ噺鐩戞祴鎺у埗鍣?add_13"
    assert data["matched_endpoint_count"] == 1
    assert data["endpoints"][0]["path"] == "/saw/rainfallmonitor/add"


def test_preview_doc_html_uses_cookie_for_group_candidates_and_does_not_return_cookie(monkeypatch) -> None:
    client = build_client()
    project = client.post("/api/v1/projects", json={"name": "Cookie Project"}).json()["data"]
    captured: list[tuple[str, str | None]] = []
    openapi_content = {
        "openapi": "3.0.0",
        "info": {"title": "Cookie Knife4j Demo", "version": "1.0.0"},
        "paths": {
            "/saw/rainfallmonitor/add": {
                "post": {
                    "tags": ["yingji"],
                    "summary": "鏂板闆ㄩ噺鐩戞祴",
                    "operationId": "addRainfallMonitor",
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    class FakeResponse:
        def __init__(self, payload: object, status_code: int = 200) -> None:
            self.status_code = status_code
            self.content = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                error = requests.HTTPError("auth error")
                error.response = self
                raise error

    def fake_get(url: str, **kwargs: object) -> FakeResponse:
        headers = kwargs.get("headers") or {}
        cookie = headers.get("Cookie") if isinstance(headers, dict) else None
        captured.append((url, cookie))
        if url.endswith("/v3/api-docs/yingji") and cookie == "JSESSIONID=abc; SESSION=xyz":
            return FakeResponse(openapi_content)
        return FakeResponse({"code": 401, "msg": "鏈兘璇诲彇鍒版湁鏁?token", "data": None})

    monkeypatch.setattr(requests, "get", fake_get)
    response = client.post(
        f"/api/v1/projects/{project['id']}/documents/preview-url",
        json={
            "name": "Cookie Knife4j Preview",
            "input_type": "auto",
            "input_content": "http://example.test/doc.html#/yingji/闆ㄩ噺鐩戞祴鎺у埗鍣?add_13",
            "api_path_filter": "/saw/rainfallmonitor/add",
            "method_filter": "POST",
            "cookie": "Cookie: JSESSIONID=abc; SESSION=xyz",
            "need_ai_parse": True,
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["resolved_spec_url"] == "http://example.test/v3/api-docs/yingji"
    assert data["matched_endpoint_count"] == 1
    assert data["endpoints"][0]["path"] == "/saw/rainfallmonitor/add"
    assert ("http://example.test/v3/api-docs/yingji", "JSESSIONID=abc; SESSION=xyz") in captured
    assert "JSESSIONID=abc" not in response.text

    saved = client.post(
        f"/api/v1/projects/{project['id']}/documents/import-url",
        json={
            "name": "Cookie Knife4j Save",
            "input_type": "auto",
            "input_content": "http://example.test/doc.html#/yingji/闆ㄩ噺鐩戞祴鎺у埗鍣?add_13",
            "api_path_filter": "/saw/rainfallmonitor/add",
            "method_filter": "POST",
            "cookie": "JSESSIONID=abc; SESSION=xyz",
            "need_ai_parse": True,
            "save_mode": "save_all",
            "endpoints": data["endpoints"],
            "selected_endpoint_keys": [],
        },
    )

    assert saved.status_code == 200
    assert "JSESSIONID=abc" not in saved.text
    saved_document = saved.json()["data"]["document"]
    assert "JSESSIONID=abc" not in saved_document["raw_content"]
    assert "JSESSIONID=abc" not in json.dumps(saved_document["parsed_data"], ensure_ascii=False)


def test_preview_doc_html_auth_warning_without_cookie(monkeypatch) -> None:
    client = build_client()
    project = client.post("/api/v1/projects", json={"name": "Auth Warning Project"}).json()["data"]

    class FakeResponse:
        def __init__(self) -> None:
            self.status_code = 200
            self.content = b'{"code":401,"msg":"\\u672a\\u80fd\\u8bfb\\u53d6\\u5230\\u6709\\u6548 token","data":null}'

        def raise_for_status(self) -> None:
            return None

    monkeypatch.setattr(requests, "get", lambda *_args, **_kwargs: FakeResponse())
    response = client.post(
        f"/api/v1/projects/{project['id']}/documents/preview-url",
        json={
            "name": "Auth Warning",
            "input_type": "auto",
            "input_content": "http://example.test/doc.html#/yingji/闆ㄩ噺鐩戞祴鎺у埗鍣?add_13",
            "need_ai_parse": True,
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["matched_endpoint_count"] == 0
    assert any("登录态" in warning for warning in data["warnings"])
    assert any("401/403" in error for error in data["errors"])


def test_preview_api_path_creates_draft_when_not_found() -> None:
    client = build_client()
    project = client.post("/api/v1/projects", json={"name": "Draft Project"}).json()["data"]

    response = client.post(
        f"/api/v1/projects/{project['id']}/documents/preview-url",
        json={
            "name": "Draft Preview",
            "input_type": "api_path",
            "input_content": "POST /unknown/path",
            "need_ai_parse": True,
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["matched_endpoint_count"] == 1
    assert data["endpoints"][0]["source"] == "draft"
    assert data["endpoints"][0]["status"] == "draft"
    assert "不会凭空补全参数" in data["warnings"][0]
