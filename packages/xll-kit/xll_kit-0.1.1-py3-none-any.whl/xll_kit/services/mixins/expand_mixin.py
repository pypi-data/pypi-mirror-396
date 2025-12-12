# xll_kit/services/mixins/expand_mixin.py
from typing import List

class ServiceExpandMixin:
    # 可在子类 override，提供更高层业务别名
    def _expand_map(self):
        return {}

    def apply_expands(self, stmt, expands: List[str] = None):
        if not expands:
            return stmt
        # 允许 service 层定义别名映射到 crud 的 expands 名
        expand_map = self._expand_map()
        resolved = []
        for e in expands:
            target = expand_map.get(e, e)
            resolved.append(target)
        return self.crud.apply_expands(stmt, resolved)
