"""
xll_kit.database - 数据库操作模块

提供SQL构建和执行功能，支持MySQL、PostgreSQL等数据库
"""

from .builders import (
    SQLBuilder,
    MySQLBuilder,
    PostgreSQLBuilder,
    SQLBuilderFactory,
    SQLResult,
)

from .executor import (
    SQLExecutor,
    BatchExecutor,
)

from .database_manager import (
    DatabaseManager,
)

from .session_manager import (
    SessionManager,
    init_session_manager,
    get_session_manager
)

from .exceptions import (
    DatabaseError,
    SQLBuilderError,
    ConnectionError,
    ExecutionError,
)

__all__ = [
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

    # SessionManager
    'SessionManager',
    'init_session_manager',
    'get_session_manager',

    # Exceptions
    'DatabaseError',
    'SQLBuilderError',
    'ConnectionError',
    'ExecutionError',
]
