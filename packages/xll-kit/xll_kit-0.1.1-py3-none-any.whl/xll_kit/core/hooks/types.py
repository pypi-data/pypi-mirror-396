from enum import Enum


class HookType(str, Enum):
    BEFORE_CREATE = "before_create"
    AFTER_CREATE = "after_create"
    BEFORE_UPDATE = "before_update"
    AFTER_UPDATE = "after_update"
    BEFORE_DELETE = "before_delete"
    AFTER_DELETE = "after_delete"

    BEFORE_GET = "before_get"
    AFTER_GET = "after_get"

    ON_ERROR = "on_error"
