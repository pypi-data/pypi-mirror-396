from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from xll_kit.models.audit_log import AuditObjectLog, AuditFieldLog


def log_audit_object(
    session: Session,
    obj: Any,
    action: str,
    user: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
):
    """
    记录对象级别审计日志（create/update/delete）
    data 可为差异 diff 或其它元信息
    """
    model_name = obj.__class__.__name__
    object_id = getattr(obj, "id", None)

    # log = AuditLog(
    #     model_name=model_name,
    #     object_id=str(object_id),
    #     action=action,
    #     user_id=str(user) if user else None,
    #     data=data or {}
    # )

    if not data or session is None:
        return

    # object log
    log = AuditObjectLog(
        obj_type=model_name,
        obj_id=obj.id,
        action=action,
        data=str(data),
    )

    session.add(log)
    session.flush()
    return log


def log_audit_fields(
    session: Session,
    obj: Any,
    diff: Dict[str, Any],
    user: Optional[str] = None,
):
    """
    字段级审计，可将字段变化逐项拆开记录
    """
    model_name = obj.__class__.__name__
    obj_id = getattr(obj, "id", None)

    for field, (old, new) in diff.items():
        log = AuditFieldLog(
            obj_type=model_name,
            obj_id=str(obj_id),
            field=field,
            old_value=str(old),
            new_value=str(new),
            action="update",
            # user_id=str(user) if user else None,
        )
        session.add(log)

    session.flush()
