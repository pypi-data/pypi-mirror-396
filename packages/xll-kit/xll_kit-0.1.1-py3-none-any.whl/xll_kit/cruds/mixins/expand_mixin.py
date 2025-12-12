# xll_kit/cruds/mixins/expand_mixin.py
from typing import Dict, Any, List
from sqlalchemy.orm import selectinload

class CrudExpandMixin:
    """
    CRUD 层扩展支持：提供 expand_map，返回 dict:name->load option
    """
    def _expand_map(self) -> Dict[str, Any]:
        # 子类 override
        return {}

    def apply_expands(self, stmt, expands: List[str] = None):
        if not expands:
            return stmt
        expand_map = self._expand_map()
        for e in expands:
            opt = expand_map.get(e)
            if opt is not None:
                stmt = stmt.options(opt)
        return stmt
