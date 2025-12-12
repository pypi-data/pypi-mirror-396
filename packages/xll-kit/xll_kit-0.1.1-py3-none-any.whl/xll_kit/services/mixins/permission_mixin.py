# xll_kit/services/mixins/permission_mixin.py
from xll_kit.core.permission.registry import permission_registry

class DataPermissionMixin:
    def apply_user_permission(self, stmt, user_context):
        # permission_registry 会返回修改后的 stmt
        return permission_registry.apply(self.crud.model.__name__, stmt, user_context)
