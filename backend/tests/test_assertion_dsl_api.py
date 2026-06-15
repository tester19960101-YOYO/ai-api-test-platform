from fastapi.testclient import TestClient

from app.main import create_app


def test_parse_assertion_dsl() -> None:
    client = TestClient(create_app())

    response = client.post("/api/v1/assertion/parse", json={"dsl": "$.code == 200"})

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["assertion"]["type"] == "business_code"
    assert data["assertion"]["path"] == "$.code"
    assert data["assertion"]["expected"] == 200


def test_to_dsl_from_assertion_json() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/assertion/to-dsl",
        json={"assertion": {"type": "json_path", "path": "$.msg", "operator": "contains", "expected": "成功"}},
    )

    assert response.status_code == 200
    assert response.json()["data"]["dsl"] == "$.msg contains 成功"


def test_parse_assertion_dsl_alias_without_v1() -> None:
    client = TestClient(create_app())

    response = client.post("/api/assertion/parse", json={"dsl": "status_code == 200"})

    assert response.status_code == 200
    assert response.json()["data"]["assertion"]["type"] == "status_code"
