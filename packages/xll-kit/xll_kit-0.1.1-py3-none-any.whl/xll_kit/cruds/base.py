from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, update, Select

from xll_kit.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class VersionConflictError(Exception):
    """乐观锁版本冲突异常"""

    def __init__(self, current_version: int, submitted_version: int):
        self.current_version = current_version
        self.submitted_version = submitted_version
        super().__init__(
            f"Version conflict: current version is {current_version}, but submitted version is {submitted_version}"
        )


class CRUDBase(Generic[ModelType]):
    """
    同步版 CRUD 基类（大厂标准 DAL）
    - 不依赖 schema
    - 不依赖 async
    - 可扩展 filters / expands / user filters
    - hooks 用于审计、字段级日志
    """

    def __init__(self, model: Type[ModelType], version_field: str = "version"):
        self.model = model
        self.version_field = version_field

    # -----------------------------
    # Hooks（由子类 or Service 实现）
    # -----------------------------
    def after_create(self, session: Session, obj: ModelType):
        ...

    def after_update(self, session: Session, obj: ModelType, before, after):
        ...

    def after_delete(self, session: Session, obj: ModelType):
        ...

    # -----------------------------
    # 查询
    # -----------------------------
    def get(self, session: Session, id: Any) -> Optional[ModelType]:
        return session.get(self.model, id)

    def get_by(self, session: Session, **filters) -> Optional[ModelType]:
        """
        根据条件获取单条记录

        Args:
            **filters: 过滤条件

        Returns:
            Model 实例或 None

        Example:
            user = repo.get_by(email='test@example.com')
        """
        stmt = select(self.model).filter_by(**filters)
        result = session.execute(stmt)
        return result.scalar_one_or_none()

    def get_multi_stmt(
            self,
            filters: Optional[Dict[str, Any]] = None,
            user: Optional[Any] = None,
            expands: Optional[List[str]] = None
    ) -> Select:
        stmt = select(self.model)
        stmt = self.apply_filters(stmt, filters)
        stmt = self.apply_user_filters(stmt, user)
        stmt = self.apply_expands(stmt, expands)
        return stmt

    def get_multi(
            self, session: Session,
            filters: Optional[Dict[str, Any]] = None,
            skip: int = 0,
            limit: int = 100,
            user: Optional[Any] = None,
            expands: Optional[List[str]] = None
    ) -> List[ModelType]:
        stmt = self.get_multi_stmt(filters, user, expands)
        stmt = stmt.offset(skip).limit(limit)
        return session.execute(stmt).scalars().all()

    # -----------------------------
    # 扩展点
    # -----------------------------
    def _sortable_fields(self):
        """
        定义允许排序的字段，避免注入
        例如: return ["id", "created_at", "updated_at", "view_count"]
        """
        return []

    def _get_expand_map(self) -> Dict[str, Any]:
        """
        定义支持的 expands 对象映射。
        子类可 override。
        例如：
            return {
                "author": selectinload(Post.author),
                "tags": selectinload(Post.tags),
            }
        """
        return {}

    def apply_filters(self, stmt, filters):
        return stmt

    def apply_user_filters(self, stmt, user):
        return stmt

    def apply_expands(self, stmt, expands: Optional[List[str]] = None) -> select:
        expand_map = self._get_expand_map()
        if not expands or not expand_map:
            return stmt
        for e in expands:
            if e in expand_map:
                stmt = stmt.options(expand_map[e])
        return stmt

    # -----------------------------
    # 创建
    # -----------------------------
    def create(self, session: Session, data: Dict[str, Any]) -> ModelType:
        obj = self.model(**data)
        session.add(obj)
        session.commit()
        session.refresh(obj)

        self.after_create(session, obj)
        return obj

    # -----------------------------
    # 更新（含乐观锁）
    # -----------------------------
    def update(
            self,
            session: Session,
            db_obj: ModelType,
            data: Dict[str, Any]
    ) -> ModelType:

        before = db_obj.__dict__.copy()

        stmt = (
            update(self.model)
            .where(self.model.id == db_obj.id)
            .values(**{k: v for k, v in data.items()})
        )

        # 乐观锁
        if self.version_field in data:
            old_v = getattr(db_obj, self.version_field)
            new_v = data[self.version_field]

            if old_v != new_v:
                raise VersionConflictError(old_v, new_v)

            stmt = stmt.where(
                getattr(self.model, self.version_field) == old_v
            ).values({self.version_field: old_v + 1})

        result = session.execute(stmt)
        if result.rowcount == 0:
            raise VersionConflictError("Version conflict")

        session.commit()
        session.refresh(db_obj)

        after = db_obj.__dict__.copy()
        self.after_update(session, db_obj, before, after)
        return db_obj

    # -----------------------------
    # 删除
    # -----------------------------
    def remove(self, session: Session, db_obj: ModelType) -> Optional[ModelType]:
        session.delete(db_obj)
        session.commit()

        self.after_delete(session, db_obj)
        return db_obj
