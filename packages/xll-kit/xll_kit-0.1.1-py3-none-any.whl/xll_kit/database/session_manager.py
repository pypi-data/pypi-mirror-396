"""
数据库 Session 管理
支持 FastAPI/Prefect/CLI 多种场景
"""
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Session 管理器
    支持多种使用场景：
    1. FastAPI 依赖注入
    2. Prefect Task
    3. CLI 脚本
    """

    def __init__(
            self,
            database_uri: str,
            pool_size: int = 10,
            max_overflow: int = 20,
            pool_timeout: int = 30,
            pool_recycle: int = 3600,
            echo: bool = False,
            future: bool = True,
    ):
        """
        初始化 Session 管理器

        Args:
            database_uri: 数据库连接 URI
            pool_size: 连接池大小
            max_overflow: 最大溢出连接数
            pool_timeout: 连接超时时间
            pool_recycle: 连接回收时间
            echo: 是否打印 SQL
            future: 使用 SQLAlchemy 2.0 风格
        """
        self.database_uri = database_uri
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._scoped_session: Optional[scoped_session] = None

        # 引擎配置
        self.engine_config = {
            'poolclass': QueuePool,
            'pool_size': pool_size,
            'max_overflow': max_overflow,
            'pool_timeout': pool_timeout,
            'pool_recycle': pool_recycle,
            'pool_pre_ping': True,
            'echo': echo,
            'future': future,
        }

    @property
    def engine(self) -> Engine:
        """延迟创建引擎"""
        if self._engine is None:
            self._engine = create_engine(self.database_uri, **self.engine_config)
            logger.info(f"Database engine created: {self._engine.dialect.name}")
        return self._engine

    @property
    def session_factory(self) -> sessionmaker:
        """Session 工厂"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )
        return self._session_factory

    @property
    def scoped_session_factory(self) -> scoped_session:
        """线程安全的 Scoped Session"""
        if self._scoped_session is None:
            self._scoped_session = scoped_session(self.session_factory)
        return self._scoped_session

    def get_session(self) -> Session:
        """
        获取新 Session（用于 FastAPI 依赖注入）

        Returns:
            Session 实例
        """
        return self.session_factory()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Session 上下文管理器（用于 Prefect Task 和 CLI）

        使用示例:
            with session_manager.session_scope() as session:
                user = session.query(User).first()
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session rollback due to: {e}")
            raise
        finally:
            session.close()

    def create_tables(self, base):
        """创建所有表"""
        base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")

    def drop_tables(self, base):
        """删除所有表"""
        base.metadata.drop_all(bind=self.engine)
        logger.warning("Database tables dropped")

    def close(self):
        """关闭所有连接"""
        if self._scoped_session:
            self._scoped_session.remove()
        if self._engine:
            self._engine.dispose()
            logger.info("Database connections closed")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()


# 全局 Session 管理器实例（可选）
_global_session_manager: Optional[SessionManager] = None


def init_session_manager(database_uri: str, **kwargs) -> SessionManager:
    """
    初始化全局 Session 管理器

    Args:
        database_uri: 数据库连接 URI
        **kwargs: 其他配置参数

    Returns:
        SessionManager 实例
    """
    global _global_session_manager
    _global_session_manager = SessionManager(database_uri, **kwargs)
    return _global_session_manager


def get_session_manager() -> SessionManager:
    """
    获取全局 Session 管理器

    Returns:
        SessionManager 实例

    Raises:
        RuntimeError: 如果未初始化
    """
    if _global_session_manager is None:
        raise RuntimeError(
            "SessionManager not initialized. "
            "Call init_session_manager() first."
        )
    return _global_session_manager