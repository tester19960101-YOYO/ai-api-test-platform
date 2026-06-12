from app.db.base import Base


def test_mvp_tables_are_registered() -> None:
    assert set(Base.metadata.tables) == {
        "project",
        "environment",
        "api_document",
        "api_endpoint",
        "test_case",
        "execution_task",
        "execution_result",
        "test_report",
        "ai_analysis_record",
    }
