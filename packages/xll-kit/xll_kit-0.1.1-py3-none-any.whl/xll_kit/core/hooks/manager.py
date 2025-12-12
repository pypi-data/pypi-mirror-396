from dataclasses import dataclass, field
from typing import Callable, List, Optional
from typing import Dict

from xll_kit.core.hooks.types import HookType


# ------------------------
# Hook 定义
# ------------------------


# HookEntry

@dataclass(order=True)
class HookItem:
    priority: int
    func: Callable = field(compare=False)
    model_names: Optional[List[str]] = field(default=None)
    actions: Optional[List[str]] = field(default=None)
    fields: Optional[List[str]] = field(default=None)

class HookManager:
    HOOK_TYPES = [
        "before_create", "after_create",
        "before_update", "after_update",
        "before_delete", "after_delete",
        "before_get", "after_get",
    ]

    def __init__(self):
        # 每种 hook 类型保持一个有序列表
        self.hooks: Dict[str, List[HookItem]] = {k.value: [] for k in HookType}

    # -------------------------------------------------

    def register(
            self,
            hook_type: HookType,
            func: Callable,
            *,
            priority: int = 0,
            model_names: Optional[List[str]] = None,
            actions: Optional[List[str]] = None,
            fields: Optional[List[str]] = None,
    ):
        """注册 Hook"""
        if hook_type not in self.hooks:
            raise ValueError(f"Unknown hook type: {hook_type}")

        item = HookItem(
            priority=priority,
            func=func,
            model_names=model_names,
            actions=actions,
            fields=fields,
        )

        self.hooks[hook_type].append(item)
        # priority 排序 越高越先执行
        self.hooks[hook_type].sort(reverse=True)

    # -------------------------------------------------
    # 执行
    # -------------------------------------------------

    def execute(
            self,
            hook_type: HookType,
            session=None,
            model_name: Optional[str] = None,
            action: Optional[str] = None,
            diff: Optional[dict] = None,
            **context,
    ):
        """执行 hook 链"""

        items = self.hooks.get(hook_type, [])

        for hook in items:
            # ------- 按 model 筛选 -------
            if hook.model_names and model_name not in hook.model_names:
                continue

            # ------- 按动作筛选 -------
            if hook.actions and action not in hook.actions:
                continue

            # ------- 按字段筛选 -------
            if hook.fields and diff:
                if not any(f in diff for f in hook.fields):
                    continue

            # 执行 hook
            hook.func(
                session=session,
                model_name=model_name,
                action=action,
                diff=diff,
                **context
            )


# 全局 hook manager
global_hook_manager = HookManager()
