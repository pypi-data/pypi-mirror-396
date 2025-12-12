from .manager import global_hook_manager
from .decorator import (
    _register,
    hook_before_get,
    hook_after_get,
    hook_before_create,
    hook_after_create,
    hook_before_update,
    hook_after_update,
    hook_before_delete,
    hook_after_delete,
    hook_on_error
)

__all__ = [
    # Audits
    "global_hook_manager",
    "_register",
    "hook_before_get",
    "hook_after_get",
    "hook_before_create",
    "hook_after_create",
    "hook_before_update",
    "hook_after_update",
    "hook_before_delete",
    "hook_after_delete",
    "hook_on_error"
]
