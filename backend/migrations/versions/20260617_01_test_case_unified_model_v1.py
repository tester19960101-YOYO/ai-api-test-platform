"""add TestCaseUnifiedModel v1 fields

Revision ID: 20260617_01
Revises:
Create Date: 2026-06-17
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260617_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("test_case", sa.Column("endpoint_name", sa.String(length=128), nullable=True, comment="Endpoint name snapshot"))
    op.add_column("test_case", sa.Column("endpoint_path", sa.String(length=512), nullable=True, comment="Endpoint path snapshot"))
    op.add_column(
        "test_case",
        sa.Column("type", sa.String(length=32), nullable=False, server_default="functional", comment="Unified test case type"),
    )
    op.add_column("test_case", sa.Column("request_data", sa.JSON(), nullable=True, comment="Unified request data"))
    op.add_column("test_case", sa.Column("dsl_assertions", sa.JSON(), nullable=True, comment="DSL assertion list"))
    op.add_column("test_case", sa.Column("coverage_tag", sa.JSON(), nullable=True, comment="Coverage tags"))
    op.add_column("test_case", sa.Column("risk_level", sa.String(length=32), nullable=True, comment="Risk level"))
    op.add_column("test_case", sa.Column("data_dependency", sa.JSON(), nullable=True, comment="Data dependency"))
    op.add_column("test_case", sa.Column("ai_metadata", sa.JSON(), nullable=True, comment="AI generation metadata"))
    op.create_index("idx_test_case_type", "test_case", ["type"])
    op.create_index("idx_test_case_priority", "test_case", ["priority"])

    op.execute(
        """
        UPDATE test_case tc
        LEFT JOIN api_endpoint ae ON tc.api_endpoint_id = ae.id
        SET
          tc.endpoint_name = COALESCE(tc.endpoint_name, ae.name),
          tc.endpoint_path = COALESCE(tc.endpoint_path, ae.path),
          tc.priority = CASE
            WHEN tc.priority = 'high' THEN 'P0'
            WHEN tc.priority = 'low' THEN 'P2'
            WHEN tc.priority IN ('P0', 'P1', 'P2') THEN tc.priority
            ELSE 'P1'
          END,
          tc.status = CASE
            WHEN tc.status = 'inactive' THEN 'disabled'
            WHEN tc.status IN ('edited', 'generated', 'disabled', 'passed', 'failed') THEN tc.status
            ELSE 'generated'
          END,
          tc.risk_level = CASE
            WHEN tc.priority = 'P0' THEN 'high'
            WHEN tc.priority = 'P2' THEN 'low'
            ELSE 'medium'
          END
        """
    )


def downgrade() -> None:
    op.drop_index("idx_test_case_priority", table_name="test_case")
    op.drop_index("idx_test_case_type", table_name="test_case")
    op.drop_column("test_case", "ai_metadata")
    op.drop_column("test_case", "data_dependency")
    op.drop_column("test_case", "risk_level")
    op.drop_column("test_case", "coverage_tag")
    op.drop_column("test_case", "dsl_assertions")
    op.drop_column("test_case", "request_data")
    op.drop_column("test_case", "type")
    op.drop_column("test_case", "endpoint_path")
    op.drop_column("test_case", "endpoint_name")
