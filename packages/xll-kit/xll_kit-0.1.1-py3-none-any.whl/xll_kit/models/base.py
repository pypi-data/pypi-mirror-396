"""
SQLAlchemy ORM Base 类
"""
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Integer, DateTime, Boolean
from sqlalchemy.orm import declarative_base, declared_attr, Mapped, mapped_column, validates

# 创建 Base 类
Base = declarative_base()


class BaseModel(Base):
    """
    基础 Model 类
    所有 ORM Model 继承此类
    """
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """自动生成表名（类名转小写）"""
        return cls.__name__.lower()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """从字典更新属性"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self) -> str:
        """字符串表示"""
        attrs = ', '.join(
            f"{col.name}={getattr(self, col.name)!r}"
            for col in self.__table__.columns
        )
        return f"<{self.__class__.__name__}({attrs})>"
