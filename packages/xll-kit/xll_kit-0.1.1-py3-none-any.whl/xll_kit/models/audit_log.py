from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from xll_kit.models import BaseModel, TimestampMixin


class AuditObjectLog(BaseModel, TimestampMixin):
    """审计日志"""

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    obj_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )
    obj_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )
    obj_version: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    action: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )
    data: Mapped[str] = mapped_column(
        String(1024),
        nullable=False
    )
    operator: Mapped[str] = mapped_column(
        String(64),
        nullable=True
    )


class AuditFieldLog(BaseModel, TimestampMixin):
    """审计日志"""

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    obj_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )
    obj_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )
    obj_version: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    field: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )
    old_value: Mapped[str] = mapped_column(
        String(1024),
        nullable=True
    )
    new_value: Mapped[str] = mapped_column(
        String(1024),
        nullable=True
    )
    operator: Mapped[str] = mapped_column(
        String(64),
        nullable=True
    )
    action: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )
