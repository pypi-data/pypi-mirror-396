import contextlib
import logging
from datetime import datetime
from typing import Optional, Any, Dict, List

from sqlalchemy import text
# 需要安装: pip install sqlalchemy[asyncio] aiosqlite click
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import DeclarativeBase

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """SQLAlchemy 基类"""
    pass


class AsyncDatabaseManager:
    """异步数据库管理器"""

    def __init__(
            self,
            database_url: str = "sqlite+aiosqlite:///./app.db",
            echo: bool = False,
            pool_size: int = 5,
            max_overflow: int = 10
    ):
        """
        初始化数据库管理器

        Args:
            database_url: 数据库连接 URL
            echo: 是否输出 SQL 语句
            pool_size: 连接池大小
            max_overflow: 连接池溢出大小
        """
        self.database_url = database_url
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker] = None
        self.echo = echo
        self.pool_size = pool_size
        self.max_overflow = max_overflow

    async def init(self):
        """初始化数据库引擎和会话工厂"""
        if self.engine is not None:
            return

        self.engine = create_async_engine(
            self.database_url,
            echo=self.echo,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_pre_ping=True,  # 连接前检查
        )

        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        logger.info(f"数据库引擎已初始化: {self.database_url}")

    async def close(self):
        """关闭数据库连接"""
        if self.engine:
            await self.engine.dispose()
            logger.info("数据库连接已关闭")

    async def create_tables(self):
        """创建所有表"""
        await self.init()
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表已创建")

    async def drop_tables(self):
        """删除所有表"""
        await self.init()
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("数据库表已删除")

    @contextlib.asynccontextmanager
    async def session(self):
        """获取数据库会话上下文管理器"""
        await self.init()
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"会话错误: {e}")
                raise
            finally:
                await session.close()

    async def execute(self, query: str, params: Optional[Dict] = None) -> Any:
        """执行原始 SQL 查询"""
        async with self.session() as session:
            result = await session.execute(text(query), params or {})
            return result

    async def fetch_one(self, query: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """查询单条记录"""
        result = await self.execute(query, params)
        row = result.fetchone()
        return dict(row._mapping) if row else None

    async def fetch_all(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """查询多条记录"""
        result = await self.execute(query, params)
        return [dict(row._mapping) for row in result.fetchall()]

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            await self.init()
            async with self.session() as session:
                await session.execute(text("SELECT 1"))
            return {
                "status": "healthy",
                "database": self.database_url,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
