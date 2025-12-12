# 语法糖
from .manager import global_hook_manager
from .types import HookType


def _register(hook_type, model: str | list[str] | None = None, actions: list[str] | None = None,
              fields: list[str] | None = None, priority=0):
    if isinstance(model, str):
        model = [model]

    def decorator(func):
        global_hook_manager.register(
            hook_type, func, model=model, actions=actions, fields=fields, priority=priority
        )
        return func

    return decorator


def hook_before_get(**kwargs): return _register(HookType.BEFORE_GET, **kwargs)


def hook_after_get(**kwargs):  return _register(HookType.AFTER_GET, **kwargs)


def hook_before_create(**kwargs): return _register(HookType.BEFORE_CREATE, **kwargs)


def hook_after_create(**kwargs):  return _register(HookType.AFTER_CREATE, **kwargs)


def hook_before_update(**kwargs): return _register(HookType.BEFORE_UPDATE, **kwargs)


def hook_after_update(**kwargs):  return _register(HookType.AFTER_UPDATE, **kwargs)


def hook_before_delete(**kwargs): return _register(HookType.BEFORE_DELETE, **kwargs)


def hook_after_delete(**kwargs):  return _register(HookType.AFTER_DELETE, **kwargs)


def hook_on_error(**kwargs):      return _register(HookType.ON_ERROR, **kwargs)
