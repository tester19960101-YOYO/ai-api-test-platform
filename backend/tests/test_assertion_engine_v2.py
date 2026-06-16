from app.core.assertion_engine_v2 import build_assertion, fuse_assertions, normalize_ai_suggestions, normalize_user_assertions


def test_fuse_assertions_prefers_user_over_swagger_and_ai() -> None:
    swagger = [
        build_assertion({"type": "business_code", "path": "$.code", "operator": "==", "expected": 200}, "swagger")
    ]
    ai = normalize_ai_suggestions(
        {"suggestions": [{"type": "json_path_equal", "path": "$.code", "expected": 1, "confidence": 0.9}]}
    )
    user = normalize_user_assertions([{"type": "json_path_equal", "path": "$.code", "expected": 0}])

    fused = fuse_assertions(swagger_assertions=swagger, ai_assertions=ai, user_assertions=user)

    code_assertion = next(item for item in fused["final_assertions"] if item["path"] == "$.code")
    assert code_assertion["source"] == "user"
    assert code_assertion["expected"] == 0
    assert all(item.get("expected") != 1 for item in fused["final_assertions"])


def test_ai_suggestions_are_disabled_by_default() -> None:
    ai = normalize_ai_suggestions({"assertions": ["$.code == 200"]})
    fused = fuse_assertions(ai_assertions=ai)

    assert fused["final_assertions"][0]["source"] == "ai"
    assert fused["final_assertions"][0]["enabled"] is False
    assert fused["final_assertions"][0]["dsl"] == "$.code == 200"


def test_user_dsl_overrides_ai_dsl() -> None:
    ai = normalize_ai_suggestions({"assertions": ["$.code == 200"]})
    user = normalize_user_assertions(["$.code == 0"])

    fused = fuse_assertions(ai_assertions=ai, user_assertions=user)

    code_assertion = next(item for item in fused["final_assertions"] if item["path"] == "$.code")
    assert code_assertion["source"] == "user"
    assert code_assertion["expected"] == 0


def test_user_dsl_allows_operator_without_spaces() -> None:
    user = normalize_user_assertions(['$.msg== "操作成功"'])

    assert user[0]["path"] == "$.msg"
    assert user[0]["operator"] == "=="
    assert user[0]["expected"] == "操作成功"


def test_invalid_user_dsl_becomes_failed_runtime_assertion() -> None:
    user = normalize_user_assertions(["not a valid assertion"])

    assert user[0]["path"] == "$.__invalid_assertion__"
    assert "parse_error" in user[0]
