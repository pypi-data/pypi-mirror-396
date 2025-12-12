# xll_kit/services/mixins/audit_mixin.py
from xll_kit.core.audit.diff import diff_model
from xll_kit.core.audit.logger import log_audit_object, log_audit_fields

class AuditServiceMixin:
    def _audit_create(self, session, obj, user=None):
        # 如果模型定义了 audit config 才记录
        log_audit_object(session, obj, action="create", user=user)

    def _audit_update(self, session, obj, before, after, user=None):
        diff = diff_model(before, after,
                          include=getattr(obj, "_audit_include", None),
                          exclude=getattr(obj, "_audit_exclude", None))
        if diff:
            log_audit_object(session, obj, action="update", data=diff, user=user)
            log_audit_fields(session, obj, diff, user=user)

    def _audit_delete(self, session, obj, before, user=None):
        log_audit_object(session, obj, action="delete", user=user)
