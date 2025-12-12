# xll_kit/services/base.py
from typing import Generic, TypeVar, Optional, Dict, Any, List
from sqlalchemy.orm import Session

from xll_kit.services.mixins.audit_mixin import AuditServiceMixin
from xll_kit.services.mixins.permission_mixin import DataPermissionMixin
from xll_kit.services.mixins.expand_mixin import ServiceExpandMixin
from xll_kit.services.mixins.sort_mixin import SortMixin
from xll_kit.services.mixins.pagination_mixin import PaginationMixin

M = TypeVar("M")

class BaseService(
    AuditServiceMixin,
    DataPermissionMixin,
    ServiceExpandMixin,
    SortMixin,
    PaginationMixin,
    Generic[M]
):
    def __init__(self, crud):
        self.crud = crud

    def get(self, session: Session, id, user=None) -> Optional[M]:
        stmt = self.crud.get_multi_stmt(filters={"id": id})
        stmt = self.apply_user_permission(stmt, user)
        stmt = self.apply_expands(stmt, [])
        result = session.execute(stmt)
        return result.scalars().first()

    def list(self, session: Session, filters=None, skip=0, limit=100, expands=None, sort=None, user=None):
        stmt = self.crud.get_multi_stmt(filters=filters, expands=expands)
        stmt = self.apply_user_permission(stmt, user)
        stmt = self.apply_expands(stmt, expands)
        stmt = self.apply_sort(stmt, sort)
        return self.paginate(session, stmt, skip, limit)

    def create(self, session: Session, data: Dict[str, Any], user=None):
        obj = self.crud.create(session, data)
        # audit
        self._audit_create(session, obj, user=user)
        return obj

    def update(self, session: Session, id, data: Dict[str, Any], user=None):
        obj = self.crud.get(session, id)
        before = obj.__dict__.copy()
        obj = self.crud.update(session, obj, data)
        after = obj.__dict__.copy()
        self._audit_update(session, obj, before, after, user=user)
        return obj

    def delete(self, session: Session, id, user=None):
        obj = self.crud.get(session, id)
        before = obj.__dict__.copy()
        self.crud.remove(session, obj)
        self._audit_delete(session, obj, before, user=user)
