# app/services/base.py
from typing import TypeVar, Generic, Dict, Any, Optional, List
from sqlalchemy import desc, asc, select, func
from sqlalchemy.orm import Session

from xll_kit.core.audit import diff_model
from xll_kit.core.hooks import global_hook_manager
from xll_kit.cruds import CRUDBase
from xll_kit.services.pagination import PaginationResult

# from xll_kit.services.hooks import HookManager

ModelType = TypeVar("ModelType")
CRUDType = TypeVar("CRUDType", bound=CRUDBase)  # 新增CRUD类型参数

class BaseService(Generic[ModelType, CRUDType]):
    def __init__(self, crud: CRUDType):
        self.crud = crud
        # self.hook_manager = HookManager()
        self.hook_manager = global_hook_manager

    # @contextmanager
    # def with_hooks(self):
    #     """上下文管理器，确保 hooks 执行"""
    #     try:
    #         yield
    #     except Exception as e:
    #         # 可以添加错误处理 hook
    #         self.hook_manager.execute('on_error', session, error=e)
    #         raise

    # ============ 基础 CRUD ============
    def get(self, session: Session, id: Any, user=None) -> Optional[ModelType]:
        obj = self.crud.get(session, id)

        self._after_get(session, obj, user)

        return obj

    def get_by(self, session: Session, user=None, **filters) -> Optional[ModelType]:
        obj = self.crud.get_by(session, **filters)
        self._after_get(session, obj, user)

        return obj

    def list(self,
             session: Session,
             filters: Optional[dict] = None,
             skip: int = 0,
             limit: int = 100,
             expands: Optional[List[str]] = None,
             user: Optional[Any] = None
             ):
        self._before_get(session, user=user)
        query = self.crud.get_multi_stmt(filters=filters, user=user, expands=expands)
        result = session.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    def create(self, session: Session, data: Dict[str, Any], user=None) -> ModelType:
        # 1. 执行前置 hooks
        # self.hook_manager.execute('before_create', session, data=data)
        self._before_create(session, data, user)

        # 2. 数据验证/转换（在 hooks 之后）
        # validated_data = self._validate_create_data(data)
        validated_data = data

        # 3. 执行业务逻辑

        # 4. 调用纯粹的 CRUD
        obj = self.crud.create(session, validated_data)

        # 5. 执行后置 hooks
        # self.hook_manager.execute('after_create', session, obj=obj, data=data)
        self._after_create(session, obj, validated_data)

        return obj

    def update(self, session: Session, id, data: dict):
        obj = self.crud.get(session, id)
        before = obj.__dict__.copy()

        self._before_update(session, obj, data)

        obj = self.crud.update(session, obj, data)

        after = obj.__dict__.copy()
        diff = diff_model(before, after)

        self._after_update(session, obj, diff)

        return obj

    def delete(self, session: Session, id):
        obj = self.crud.get(session, id)
        before = obj.__dict__.copy()

        self._before_delete(session, obj, before)

        self.crud.remove(session, obj)

        self._after_delete(session, obj, before)

    # ============ HOOKS ============

    def _before_get(self, session: Session, user=None):
        global_hook_manager.execute(
            "before_get",
            session=session,
            model_name=self.crud.model.__name__,
            user=user
        )

    def _after_get(self, session: Session, obj: ModelType = None, user=None):
        global_hook_manager.execute(
            "after_get",
            session=session,
            model_name=self.crud.model.__name__,
            obj=obj,
            user=user
        )

    def _before_create(self, session: Session, data: dict, user=None):
        global_hook_manager.execute(
            "before_create",
            session=session,
            model_name=self.crud.model.__name__,
            action="create",
            data=data,
            user=user
        )

    def _after_create(self, session: Session, obj: ModelType, data: dict):
        global_hook_manager.execute(
            "after_create",
            session=session,
            model_name=self.crud.model.__name__,
            action="create",
            obj=obj,
            data=data
        )

    def _before_update(self, session: Session, obj: ModelType, update_data: dict):
        global_hook_manager.execute(
            "before_update",
            session=session,
            model_name=self.crud.model.__name__,
            action="update",
            obj=obj,
            data=update_data
        )

    def _after_update(self, session: Session, obj: ModelType, diff: dict):
        global_hook_manager.execute(
            "after_update",
            session=session,
            model_name=self.crud.model.__name__,
            action="update",
            obj=obj,
            diff=diff
        )

    def _before_delete(self, session: Session, obj: ModelType, data: dict):
        global_hook_manager.execute(
            "before_delete",
            session=session,
            model_name=self.crud.model.__name__,
            action="delete",
            obj=obj,
            data=data
        )

    def _after_delete(self, session: Session, obj: ModelType, data: dict):
        global_hook_manager.execute(
            "after_delete",
            session=session,
            model_name=self.crud.model.__name__,
            action="delete",
            obj=obj,
            data=data
        )

    # ============ 高级功能 ============
    def page(
            self,
            session: Session,
            filters: Optional[dict] = None,
            skip: int = 0,
            limit: int = 100,
            expands: Optional[List[str]] = None,
            fields: Optional[List[str]] = None,
            sort: Optional[str] = None,
            user: Optional[Any] = None
    ):
        """
        通用分页查询
        ---------------------------------
        Args:
            session: SQLAlchemy Session
            filters: 查询过滤条件
            skip: 偏移量（分页起点）
            limit: 分页大小
            expands: 展开关联（selectinload）
            fields: 返回字段控制
            sort: 排序字符串，如 "-created_at,title"
            user: 用户上下文
        Returns:
            PaginationResult: { items, total, page, limit }
        """
        query = self.crud.get_multi_stmt(filters=filters, user=user, expands=expands)

        if sort:
            query = self._apply_sort(query, sort)

        # 计算总数
        total_stmt = select(func.count()).select_from(query.subquery())
        total = session.scalar(total_stmt) or 0

        # items
        items_stmt = query.offset(skip).limit(limit)
        result = session.execute(items_stmt)
        items = result.scalars().all()

        return PaginationResult(items=items, total=total, page=skip // limit + 1, limit=limit)

    # ============ 内部辅助 ============

    # ============ 内部排序工具 ============

    def _apply_sort(self, query, sort: str):
        """
        解析 sort 参数并动态应用排序
        ?sort=-created_at,title
        """
        sort_items = [s.strip() for s in sort.split(",") if s.strip()]
        sortable_fields = getattr(self.crud, "_sortable_fields", lambda: [])()

        order_clauses = []
        for field in sort_items:
            direction = desc if field.startswith("-") else asc
            field_name = field.lstrip("-")
            if field_name in sortable_fields:
                order_clauses.append(direction(getattr(self.crud.model, field_name)))
        if order_clauses:
            query = query.order_by(*order_clauses)
        return query
