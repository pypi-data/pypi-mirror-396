"""
数据库管理器 - 完整CRUD封装
适用于非Prefect场景，提供便捷的高级API
"""
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.pool import QueuePool
import logging

from .builders import SQLBuilderFactory, SQLResult
from .exceptions import (
    DatabaseError,
    TableNotFoundError,
    ValidationError,
    ExecutionError
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    数据库管理器 - 完整功能版

    特点：
    - 维护连接池和元数据缓存
    - 提供便捷的CRUD方法
    - 适合在非Prefect环境使用
    - 不适合在Prefect Task间传递（包含状态）
    """

    def __init__(
            self,
            database_uri: str,
            pool_size: int = 10,
            max_overflow: int = 20,
            pool_timeout: int = 30,
            echo: bool = False
    ):
        """
        初始化数据库管理器

        Args:
            database_uri: 数据库连接URI
            pool_size: 连接池大小
            max_overflow: 最大溢出连接数
            pool_timeout: 连接超时时间(秒)
            echo: 是否打印SQL
        """
        try:
            self.engine = create_engine(
                database_uri,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_timeout=pool_timeout,
                pool_pre_ping=True,
                echo=echo
            )

            self.metadata = MetaData()
            self.metadata.reflect(bind=self.engine)
            self._table_cache = {}

            dialect_name = self.engine.dialect.name
            self.builder = SQLBuilderFactory.get_builder(dialect_name)

            logger.info(f"DatabaseManager initialized for {dialect_name}")

        except Exception as e:
            logger.error(f"Failed to initialize DatabaseManager: {e}")
            raise DatabaseError(f"Initialization failed: {e}")

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

    def get_table(self, table_name: str) -> Table:
        """获取表对象（带缓存）"""
        if table_name not in self._table_cache:
            if table_name not in self.metadata.tables:
                raise TableNotFoundError(table_name)
            self._table_cache[table_name] = self.metadata.tables[table_name]
        return self._table_cache[table_name]

    def _filter_data(self, table: Table, data: Dict[str, Any]) -> Dict[str, Any]:
        """过滤无效字段"""
        valid_columns = {col.name for col in table.columns}
        filtered = {k: v for k, v in data.items() if k in valid_columns}

        invalid_cols = set(data.keys()) - valid_columns
        if invalid_cols:
            logger.warning(f"Ignored invalid columns: {invalid_cols}")

        return filtered

    def _validate_data(self, data: Any, data_type: str = "data"):
        """验证数据"""
        if not data:
            raise ValidationError(f"{data_type} cannot be empty")

    def execute(self, sql_result: SQLResult) -> int:
        """执行SQL语句"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(sql_result.sql), sql_result.params)
                affected = result.rowcount if hasattr(result, 'rowcount') else 0
                logger.info(f"SQL executed. Rows affected: {affected}")
                return affected
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            raise ExecutionError(str(e), sql_result.sql, sql_result.params)

    # ==================== CRUD 方法 ====================

    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        """
        插入单条数据

        Args:
            table_name: 表名
            data: 数据字典

        Returns:
            影响的行数
        """
        self._validate_data(data)
        table = self.get_table(table_name)
        filtered_data = self._filter_data(table, data)

        sql_result = self.builder.build_insert(table, filtered_data)
        return self.execute(sql_result)

    def insert_many(
            self,
            table_name: str,
            data_list: List[Dict[str, Any]],
            batch_size: int = 1000
    ) -> int:
        """
        批量插入数据

        Args:
            table_name: 表名
            data_list: 数据列表
            batch_size: 批次大小

        Returns:
            总影响行数
        """
        self._validate_data(data_list, "data_list")
        table = self.get_table(table_name)

        total_affected = 0
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            filtered_batch = [self._filter_data(table, d) for d in batch]

            sql_result = self.builder.build_batch_insert(table, filtered_batch)
            affected = self.execute(sql_result)
            total_affected += affected

            logger.info(f"Batch {i // batch_size + 1} inserted: {affected} rows")

        return total_affected

    def upsert(
            self,
            table_name: str,
            data: Dict[str, Any],
            conflict_target: Optional[List[str]] = None
    ) -> int:
        """
        Upsert单条数据

        Args:
            table_name: 表名
            data: 数据字典
            conflict_target: 冲突检测列

        Returns:
            影响的行数
        """
        self._validate_data(data)
        table = self.get_table(table_name)
        filtered_data = self._filter_data(table, data)

        if not conflict_target:
            conflict_target = [key.name for key in table.primary_key]

        sql_result = self.builder.build_upsert(table, filtered_data, conflict_target)
        return self.execute(sql_result)

    def upsert_many(
            self,
            table_name: str,
            data_list: List[Dict[str, Any]],
            conflict_target: Optional[List[str]] = None,
            batch_size: int = 1000
    ) -> int:
        """
        批量Upsert数据

        Args:
            table_name: 表名
            data_list: 数据列表
            conflict_target: 冲突检测列
            batch_size: 批次大小

        Returns:
            总影响行数
        """
        self._validate_data(data_list, "data_list")
        table = self.get_table(table_name)

        if not conflict_target:
            conflict_target = [key.name for key in table.primary_key]

        total_affected = 0
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            filtered_batch = [self._filter_data(table, d) for d in batch]

            sql_result = self.builder.build_batch_upsert(table, filtered_batch, conflict_target)
            affected = self.execute(sql_result)
            total_affected += affected

            logger.info(f"Batch {i // batch_size + 1} upserted: {affected} rows")

        return total_affected

    def update(
            self,
            table_name: str,
            data: Dict[str, Any],
            where: Dict[str, Any]
    ) -> int:
        """
        更新数据

        Args:
            table_name: 表名
            data: 更新的数据
            where: WHERE条件

        Returns:
            影响的行数
        """
        self._validate_data(data, "data")
        self._validate_data(where, "where")

        table = self.get_table(table_name)
        filtered_data = self._filter_data(table, data)

        sql_result = self.builder.build_update(table, filtered_data, where)
        return self.execute(sql_result)

    def update_many(
            self,
            table_name: str,
            data_list: List[Dict[str, Any]],
            key_columns: Optional[List[str]] = None
    ) -> int:
        """
        批量更新数据

        Args:
            table_name: 表名
            data_list: 数据列表
            key_columns: 键列

        Returns:
            影响的行数
        """
        self._validate_data(data_list, "data_list")
        table = self.get_table(table_name)

        if not key_columns:
            key_columns = [key.name for key in table.primary_key]

        filtered_batch = [self._filter_data(table, d) for d in data_list]
        sql_result = self.builder.build_batch_update(table, filtered_batch, key_columns)
        return self.execute(sql_result)

    def delete(self, table_name: str, conditions: Dict[str, Any]) -> int:
        """
        删除数据

        Args:
            table_name: 表名
            conditions: 删除条件

        Returns:
            影响的行数
        """
        self._validate_data(conditions, "conditions")
        table = self.get_table(table_name)

        sql_result = self.builder.build_delete(table, conditions)
        return self.execute(sql_result)

    def query(
            self,
            sql: str,
            params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        执行查询

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
            raise ExecutionError(str(e), sql, params)

    def query_one(
            self,
            sql: str,
            params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """查询单条记录"""
        results = self.query(sql, params)
        return results[0] if results else None

    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()