import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text


class AuditLogRouter:
    """
    动态路由审计日志到 audit_log_YYYYMM 的真实分表
    """

    def get_table_name(self, dt: datetime.datetime | None = None):
        dt = dt or datetime.datetime.utcnow()
        suffix = dt.strftime("%Y%m")
        return f"audit_log_{suffix}"

    def ensure_table_exists(self, session: Session, table_name: str):
        """
        自动建表（基于 audit_log 模板），只在第一次使用时建一次
        """
        session.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                LIKE audit_log INCLUDING ALL
            )
        """))
        session.commit()

    def insert(self, session: Session, table_name: str, data: dict):
        """
        直接写入分表
        """
        columns = ", ".join(data.keys())
        place = ", ".join([f":{k}" for k in data.keys()])
        sql = text(f"INSERT INTO {table_name} ({columns}) VALUES ({place})")
        session.execute(sql, data)
