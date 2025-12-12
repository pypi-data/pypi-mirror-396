"""
xll_kit - 数据库操作工具包

提供SQL构建、执行和Prefect集成功能
支持MySQL、PostgreSQL等主流数据库

Author: Your Name
License: MIT
"""

from .version import __version__

# Database module
from .database import (
    # Builders
    SQLBuilder,
    MySQLBuilder,
    PostgreSQLBuilder,
    SQLBuilderFactory,
    SQLResult,

    # Executors
    SQLExecutor,
    BatchExecutor,

    # Manager
    DatabaseManager,

    # Exceptions
    DatabaseError,
    SQLBuilderError,
    ConnectionError,
    ExecutionError,
)

# Utils
from .utils import (
    setup_logger,
    get_logger,
    configure_sqlalchemy_logging,
)

__all__ = [
    # Version
    '__version__',

    # Builders
    'SQLBuilder',
    'MySQLBuilder',
    'PostgreSQLBuilder',
    'SQLBuilderFactory',
    'SQLResult',

    # Executors
    'SQLExecutor',
    'BatchExecutor',

    # Manager
    'DatabaseManager',

    # Exceptions
    'DatabaseError',
    'SQLBuilderError',
    'ConnectionError',
    'ExecutionError',

    # Utils
    'setup_logger',
    'get_logger',
    'configure_sqlalchemy_logging',
]


# 快捷导入
def quick_setup(database_uri: str, log_level: str = 'INFO'):
    """
    快速设置数据库管理器和日志

    Args:
        database_uri: 数据库连接URI
        log_level: 日志级别

    Returns:
        DatabaseManager实例

    Example:
        >>> from xll_kit import quick_setup
        >>> db = quick_setup('mysql://user:pass@localhost/dbname')
        >>> db.insert('users', {'name': 'Alice', 'age': 25})
    """
    setup_logger('xll_kit', level=log_level)
    return DatabaseManager(database_uri)