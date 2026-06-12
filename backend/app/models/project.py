from sqlalchemy import JSON, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin
from app.models.types import BigIntPrimaryKey


class Project(TimestampMixin, Base):
    __tablename__ = "project"
    __table_args__ = (
        Index("idx_project_status", "status"),
        {"comment": "项目表"},
    )

    id: Mapped[int] = mapped_column(BigIntPrimaryKey, primary_key=True, autoincrement=True, comment="主键ID")
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="项目名称")
    description: Mapped[str | None] = mapped_column(Text, comment="项目描述")
    owner_name: Mapped[str | None] = mapped_column(String(128), comment="项目负责人")
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False, comment="项目状态")
    config: Mapped[dict | None] = mapped_column(JSON, comment="项目配置")

    environments: Mapped[list["Environment"]] = relationship(back_populates="project")
    api_documents: Mapped[list["ApiDocument"]] = relationship(back_populates="project")
    api_endpoints: Mapped[list["ApiEndpoint"]] = relationship(back_populates="project")
    test_cases: Mapped[list["TestCase"]] = relationship(back_populates="project")
    execution_tasks: Mapped[list["ExecutionTask"]] = relationship(back_populates="project")
    test_reports: Mapped[list["TestReport"]] = relationship(back_populates="project")
    ai_analysis_records: Mapped[list["AiAnalysisRecord"]] = relationship(back_populates="project")
