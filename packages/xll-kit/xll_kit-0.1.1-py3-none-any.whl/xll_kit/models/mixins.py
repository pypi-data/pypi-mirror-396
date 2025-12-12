from datetime import datetime

from sqlalchemy import Integer, DateTime, Boolean
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, validates

# 创建 Base 类
Base = declarative_base()


class TimestampMixin:
    """时间戳 Mixin"""
    # 创建和更新时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(),  # 使用lambda
        # default=mapped_column(server_default=func.now()),
        # server_default=func.now(),
        nullable=True,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(),  # 使用lambda
        onupdate=lambda: datetime.now(),  # 使用lambda
        # default=mapped_column(server_default=func.now()),
        # server_default=func.now(),
        # onupdate=func.now(),
        nullable=True,
        comment="更新时间"
    )

    # created_by: Mapped[str] = mapped_column(
    #     String(32),
    #     nullable=True
    # )
    # updated_by: Mapped[str] = mapped_column(
    #     String(32),
    #     nullable=True
    # )


class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="删除时间"
    )

    def mark_deleted(self):
        self.is_deleted = True
        self.deleted_at = datetime.now()


class VersionMixin:
    """版本 Mixin"""
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=True)

    @validates('version')
    def validate_version(self, key, version):
        if self.version > version:
            raise ValueError("Version conflict")
        return version

    __mapper_args__ = {
        "version_id_col": version
    }


class AuditMixin:
    _audit_include = []
    _audit_exclude = ["id", "created_at", "updated_at"]

    def get_audit_fields(self):
        fields = set(self.__dict__.keys()) - set(self._audit_exclude)
        if self._audit_include:
            fields |= set(self._audit_include)
        return fields
