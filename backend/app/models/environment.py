from sqlalchemy import JSON, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin
from app.models.types import BigIntPrimaryKey


class Environment(TimestampMixin, Base):
    __tablename__ = "environment"
    __table_args__ = (
        Index("idx_environment_project_id", "project_id"),
        Index("idx_environment_project_default", "project_id", "is_default"),
        Index("idx_environment_status", "status"),
        {"comment": "环境配置表"},
    )

    id: Mapped[int] = mapped_column(BigIntPrimaryKey, primary_key=True, autoincrement=True, comment="主键ID")
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, comment="项目ID")
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="环境名称")
    base_url: Mapped[str] = mapped_column(String(512), nullable=False, comment="环境基础URL")
    variables: Mapped[dict | None] = mapped_column(JSON, comment="环境变量")
    headers: Mapped[dict | None] = mapped_column(JSON, comment="公共请求头")
    is_default: Mapped[bool] = mapped_column(default=False, nullable=False, comment="是否默认环境")
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False, comment="环境状态")

    project: Mapped["Project"] = relationship(back_populates="environments")
    execution_tasks: Mapped[list["ExecutionTask"]] = relationship(back_populates="environment")
