"""
SQL执行器 - 轻量级设计，适合Prefect Task使用
"""
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.engine import Engine
import logging

from .builders import SQLResult

logger = logging.getLogger(__name__)


class SQLExecutor:
    """
    轻量级SQL执行器
    - 适合在Prefect Task中使用
    - 每次执行都创建新连接，避免状态问题
    - 支持从配置或环境变量初始化
    """

    def __init__(self, database_uri: str, echo: bool = False):
        """
        初始化执行器

        Args:
            database_uri: 数据库连接URI
            echo: 是否打印SQL语句
        """
        self.database_uri = database_uri
        self.echo = echo
        self._engine: Optional[Engine] = None
        self._metadata: Optional[MetaData] = None

    @property
    def engine(self) -> Engine:
        """延迟创建engine"""
        if self._engine is None:
            self._engine = create_engine(
                self.database_uri,
                echo=self.echo,
                pool_pre_ping=True,  # 连接前检查
                pool_recycle=3600,  # 1小时回收连接
            )
        return self._engine

    @property
    def metadata(self) -> MetaData:
        """延迟加载元数据"""
        if self._metadata is None:
            self._metadata = MetaData()
            self._metadata.reflect(bind=self.engine)
        return self._metadata

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'SQLExecutor':
        """从配置字典创建"""
        return cls(
            database_uri=config['database_uri'],
            echo=config.get('echo', False)
        )

    @classmethod
    def from_env(cls,
                 uri_key: str = 'DATABASE_URI',
                 echo: bool = False) -> 'SQLExecutor':
        """从环境变量创建"""
        import os
        database_uri = os.getenv(uri_key)
        if not database_uri:
            raise ValueError(f"Environment variable {uri_key} not found")
        return cls(database_uri=database_uri, echo=echo)

    def get_table(self, table_name: str) -> Table:
        """获取表对象"""
        if table_name not in self.metadata.tables:
            raise ValueError(f"Table '{table_name}' not found in database")
        return self.metadata.tables[table_name]

    @contextmanager
    def get_connection(self):
        """获取数据库连接上下文"""
        conn = self.engine.connect()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise
        finally:
            conn.close()

    def execute(self, sql_result: SQLResult) -> int:
        """
        执行SQL语句

        Args:
            sql_result: SQLResult对象

        Returns:
            影响的行数
        """
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(sql_result.sql), sql_result.params)
                affected = result.rowcount if hasattr(result, 'rowcount') else 0
                logger.info(f"SQL executed. Rows affected: {affected}")
                return affected
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            logger.error(f"SQL: {sql_result.sql[:200]}")
            raise

    def execute_many(self, sql_results: List[SQLResult]) -> int:
        """
        批量执行多个SQL语句（同一事务）

        Args:
            sql_results: SQLResult列表

        Returns:
            总影响行数
        """
        total_affected = 0
        try:
            with self.get_connection() as conn:
                for sql_result in sql_results:
                    result = conn.execute(text(sql_result.sql), sql_result.params)
                    affected = result.rowcount if hasattr(result, 'rowcount') else 0
                    total_affected += affected
                logger.info(f"Executed {len(sql_results)} statements. Total rows: {total_affected}")
                return total_affected
        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            raise

    def query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        执行查询并返回结果

        Args:
            sql: SQL查询语句
            params: 参数字典

        Returns:
            查询结果列表
        """
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(sql), params or {})
                rows = result.fetchall()

                if rows:
                    columns = result.keys()
                    return [dict(zip(columns, row)) for row in rows]
                return []
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise

    def query_one(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """查询单条记录"""
        results = self.query(sql, params)
        return results[0] if results else None

    def close(self):
        """关闭连接"""
        if self._engine:
            self._engine.dispose()
            logger.info("Database connection closed")


class BatchExecutor:
    """
    批量执行器 - 用于大数据量操作
    自动分批处理，避免内存溢出
    """

    def __init__(self, executor: SQLExecutor, batch_size: int = 1000):
        """
        初始化批量执行器

        Args:
            executor: SQL执行器
            batch_size: 批次大小
        """
        self.executor = executor
        self.batch_size = batch_size

    def execute_batches(self, sql_results: List[SQLResult]) -> int:
        """
        分批执行SQL语句

        Args:
            sql_results: SQLResult列表

        Returns:
            总影响行数
        """
        total_affected = 0
        total_batches = (len(sql_results) + self.batch_size - 1) // self.batch_size

        logger.info(f"Starting batch execution: {len(sql_results)} statements in {total_batches} batches")

        for i in range(0, len(sql_results), self.batch_size):
            batch = sql_results[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1

            try:
                affected = self.executor.execute_many(batch)
                total_affected += affected
                logger.info(f"Batch {batch_num}/{total_batches} completed. Rows: {affected}")
            except Exception as e:
                logger.error(f"Batch {batch_num}/{total_batches} failed: {e}")
                raise

        logger.info(f"All batches completed. Total rows: {total_affected}")
        return total_affected