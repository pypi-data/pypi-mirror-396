# xll_kit/cruds/mixins/filter_mixin.py
from typing import Dict, Any
from sqlalchemy import select

class FilterMixin:
    """
    提供基础 filter 功能，子类可 override `_allowed_filters`.
    filters: dict like {"name": "alice", "status": 1}
    """
    def _allowed_filters(self):
        # 子类 override 返回可接受字段列表
        return []

    def apply_filters(self, stmt, filters: Dict[str, Any] = None):
        if not filters:
            return stmt
        for k, v in filters.items():
            if v is None:
                continue
            if k not in self._allowed_filters():
                continue
            col = getattr(self.model, k, None)
            if col is None:
                continue
            stmt = stmt.where(col == v)
        return stmt
