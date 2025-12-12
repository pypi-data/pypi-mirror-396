"""
数据库操作异常类
"""


class DatabaseError(Exception):
    """数据库操作基础异常"""
    pass


class SQLBuilderError(DatabaseError):
    """SQL构建异常"""
    pass


class ConnectionError(DatabaseError):
    """数据库连接异常"""
    pass


class ExecutionError(DatabaseError):
    """SQL执行异常"""

    def __init__(self, message: str, sql: str = None, params: dict = None):
        super().__init__(message)
        self.sql = sql
        self.params = params

    def __str__(self):
        base_msg = super().__str__()
        if self.sql:
            return f"{base_msg}\nSQL: {self.sql[:200]}..."
        return base_msg


class ValidationError(DatabaseError):
    """数据验证异常"""
    pass


class TableNotFoundError(DatabaseError):
    """表不存在异常"""

    def __init__(self, table_name: str):
        self.table_name = table_name
        super().__init__(f"Table '{table_name}' not found in database")