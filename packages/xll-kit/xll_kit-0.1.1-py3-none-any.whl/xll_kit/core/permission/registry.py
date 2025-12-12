from typing import Callable, Dict, List, Any
from sqlalchemy import Select


class PermissionRegistry:
    """
    中央权限注册表
    支持：
        - per model 权限规则
        - 每个 model 可注册多个规则，按顺序执行
        - rule: Callable[[Select, user_context], Select]
    """
    def __init__(self):
        self._rules: Dict[str, List[Callable[[Select, Any], Select]]] = {}

    def register(self, model_name: str, rule: Callable[[Select, Any], Select]):
        model_name = model_name.lower()
        if model_name not in self._rules:
            self._rules[model_name] = []
        self._rules[model_name].append(rule)

    def apply(self, model_name: str, stmt: Select, user_context: Any) -> Select:
        model_name = model_name.lower()
        if model_name not in self._rules:
            return stmt

        for rule in self._rules[model_name]:
            stmt = rule(stmt, user_context)
        return stmt


permission_registry = PermissionRegistry()
