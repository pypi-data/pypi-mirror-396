"""
SQL构建器模块 - 纯函数式设计，适合Prefect使用
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from dataclasses import dataclass
from sqlalchemy import Table


@dataclass
class SQLResult:
    """SQL构建结果"""
    sql: str
    params: Dict[str, Any]

    def __repr__(self):
        return f"SQLResult(sql={self.sql[:50]}..., params={len(self.params)} items)"


class SQLBuilder(ABC):
    """SQL构建器基类 - 无状态设计"""

    @abstractmethod
    def build_insert(self, table: Table, data: Dict[str, Any]) -> SQLResult:
        """构建INSERT语句"""
        pass

    @abstractmethod
    def build_batch_insert(self, table: Table, data_list: List[Dict[str, Any]]) -> SQLResult:
        """构建批量INSERT"""
        pass

    @abstractmethod
    def build_upsert(self, table: Table, data: Dict[str, Any],
                     conflict_target: List[str]) -> SQLResult:
        """构建UPSERT语句"""
        pass

    @abstractmethod
    def build_batch_upsert(self, table: Table, data_list: List[Dict[str, Any]],
                           conflict_target: List[str]) -> SQLResult:
        """构建批量UPSERT"""
        pass

    @abstractmethod
    def build_update(self, table: Table, data: Dict[str, Any],
                     where: Dict[str, Any]) -> SQLResult:
        """构建UPDATE语句"""
        pass

    @abstractmethod
    def build_batch_update(self, table: Table, data_list: List[Dict[str, Any]],
                           key_columns: List[str]) -> SQLResult:
        """构建批量UPDATE"""
        pass

    @abstractmethod
    def build_delete(self, table: Table, conditions: Dict[str, Any]) -> SQLResult:
        """构建DELETE语句"""
        pass

    def _get_columns(self, data_list: List[Dict[str, Any]]) -> List[str]:
        """提取列名"""
        if not data_list:
            return []
        return list(data_list[0].keys())


class MySQLBuilder(SQLBuilder):
    """MySQL SQL构建器"""

    def build_insert(self, table: Table, data: Dict[str, Any]) -> SQLResult:
        columns = ", ".join(data.keys())
        placeholders = ", ".join([f":{k}" for k in data.keys()])
        sql = f"INSERT INTO {table.name} ({columns}) VALUES ({placeholders})"
        return SQLResult(sql=sql, params=data)

    def build_batch_insert(self, table: Table, data_list: List[Dict[str, Any]]) -> SQLResult:
        if not data_list:
            raise ValueError("data_list cannot be empty")

        columns = self._get_columns(data_list)
        col_str = ", ".join(columns)

        values_parts = []
        params = {}

        for idx, data in enumerate(data_list):
            placeholders = []
            for col in columns:
                param_name = f"{col}_{idx}"
                placeholders.append(f":{param_name}")
                params[param_name] = data.get(col)
            values_parts.append(f"({', '.join(placeholders)})")

        sql = f"INSERT INTO {table.name} ({col_str}) VALUES {', '.join(values_parts)}"
        return SQLResult(sql=sql, params=params)

    def build_upsert(self, table: Table, data: Dict[str, Any],
                     conflict_target: List[str]) -> SQLResult:
        insert_result = self.build_insert(table, data)

        update_parts = []
        for col in data.keys():
            if col not in conflict_target:
                update_parts.append(f"{col} = VALUES({col})")

        if update_parts:
            sql = f"{insert_result.sql} ON DUPLICATE KEY UPDATE {', '.join(update_parts)}"
        else:
            sql = insert_result.sql

        return SQLResult(sql=sql, params=insert_result.params)

    def build_batch_upsert(self, table: Table, data_list: List[Dict[str, Any]],
                           conflict_target: List[str]) -> SQLResult:
        insert_result = self.build_batch_insert(table, data_list)

        columns = self._get_columns(data_list)
        update_parts = [f"{col} = VALUES({col})" for col in columns if col not in conflict_target]

        if update_parts:
            sql = f"{insert_result.sql} ON DUPLICATE KEY UPDATE {', '.join(update_parts)}"
        else:
            sql = insert_result.sql

        return SQLResult(sql=sql, params=insert_result.params)

    def build_update(self, table: Table, data: Dict[str, Any],
                     where: Dict[str, Any]) -> SQLResult:
        set_parts = [f"{k} = :set_{k}" for k in data.keys()]
        where_parts = [f"{k} = :where_{k}" for k in where.keys()]

        sql = f"UPDATE {table.name} SET {', '.join(set_parts)} WHERE {' AND '.join(where_parts)}"

        params = {f"set_{k}": v for k, v in data.items()}
        params.update({f"where_{k}": v for k, v in where.items()})

        return SQLResult(sql=sql, params=params)

    def build_batch_update(self, table: Table, data_list: List[Dict[str, Any]],
                           key_columns: List[str]) -> SQLResult:
        if not data_list:
            raise ValueError("data_list cannot be empty")

        columns = self._get_columns(data_list)
        params = {}

        # 构建CASE WHEN语句
        update_lines = []
        for col in columns:
            if col not in key_columns:
                case_parts = [f"{col} = CASE"]
                for idx, data in enumerate(data_list):
                    when_conditions = []
                    for key_col in key_columns:
                        param_name = f"{key_col}_{idx}"
                        when_conditions.append(f"{key_col} = :{param_name}")
                        params[param_name] = data[key_col]

                    value_param = f"{col}_val_{idx}"
                    params[value_param] = data[col]
                    case_parts.append(f"WHEN {' AND '.join(when_conditions)} THEN :{value_param}")

                case_parts.append(f"ELSE {col} END")
                update_lines.append(" ".join(case_parts))

        # 构建WHERE条件
        where_parts = []
        for idx, data in enumerate(data_list):
            conditions = [f"{kc} = :{kc}_{idx}" for kc in key_columns]
            where_parts.append(f"({' AND '.join(conditions)})")

        sql = f"UPDATE {table.name} SET {', '.join(update_lines)} WHERE {' OR '.join(where_parts)}"
        return SQLResult(sql=sql, params=params)

    def build_delete(self, table: Table, conditions: Dict[str, Any]) -> SQLResult:
        where_parts = [f"{k} = :{k}" for k in conditions.keys()]
        sql = f"DELETE FROM {table.name} WHERE {' AND '.join(where_parts)}"
        return SQLResult(sql=sql, params=conditions)


class PostgreSQLBuilder(SQLBuilder):
    """PostgreSQL SQL构建器"""

    def build_insert(self, table: Table, data: Dict[str, Any]) -> SQLResult:
        columns = ", ".join(data.keys())
        placeholders = ", ".join([f":{k}" for k in data.keys()])
        sql = f"INSERT INTO {table.name} ({columns}) VALUES ({placeholders})"
        return SQLResult(sql=sql, params=data)

    def build_batch_insert(self, table: Table, data_list: List[Dict[str, Any]]) -> SQLResult:
        if not data_list:
            raise ValueError("data_list cannot be empty")

        columns = self._get_columns(data_list)
        col_str = ", ".join(columns)

        values_parts = []
        params = {}

        for idx, data in enumerate(data_list):
            placeholders = []
            for col in columns:
                param_name = f"{col}_{idx}"
                placeholders.append(f":{param_name}")
                params[param_name] = data.get(col)
            values_parts.append(f"({', '.join(placeholders)})")

        sql = f"INSERT INTO {table.name} ({col_str}) VALUES {', '.join(values_parts)}"
        return SQLResult(sql=sql, params=params)

    def build_upsert(self, table: Table, data: Dict[str, Any],
                     conflict_target: List[str]) -> SQLResult:
        insert_result = self.build_insert(table, data)

        conflict_clause = ", ".join(conflict_target)
        update_parts = [f"{col} = EXCLUDED.{col}" for col in data.keys()
                        if col not in conflict_target]

        if update_parts:
            sql = f"{insert_result.sql} ON CONFLICT ({conflict_clause}) DO UPDATE SET {', '.join(update_parts)}"
        else:
            sql = f"{insert_result.sql} ON CONFLICT ({conflict_clause}) DO NOTHING"

        return SQLResult(sql=sql, params=insert_result.params)

    def build_batch_upsert(self, table: Table, data_list: List[Dict[str, Any]],
                           conflict_target: List[str]) -> SQLResult:
        insert_result = self.build_batch_insert(table, data_list)

        conflict_clause = ", ".join(conflict_target)
        columns = self._get_columns(data_list)
        update_parts = [f"{col} = EXCLUDED.{col}" for col in columns
                        if col not in conflict_target]

        if update_parts:
            sql = f"{insert_result.sql} ON CONFLICT ({conflict_clause}) DO UPDATE SET {', '.join(update_parts)}"
        else:
            sql = f"{insert_result.sql} ON CONFLICT ({conflict_clause}) DO NOTHING"

        return SQLResult(sql=sql, params=insert_result.params)

    def build_update(self, table: Table, data: Dict[str, Any],
                     where: Dict[str, Any]) -> SQLResult:
        set_parts = [f"{k} = :set_{k}" for k in data.keys()]
        where_parts = [f"{k} = :where_{k}" for k in where.keys()]

        sql = f"UPDATE {table.name} SET {', '.join(set_parts)} WHERE {' AND '.join(where_parts)}"

        params = {f"set_{k}": v for k, v in data.items()}
        params.update({f"where_{k}": v for k, v in where.items()})

        return SQLResult(sql=sql, params=params)

    def build_batch_update(self, table: Table, data_list: List[Dict[str, Any]],
                           key_columns: List[str]) -> SQLResult:
        if not data_list:
            raise ValueError("data_list cannot be empty")

        columns = self._get_columns(data_list)
        params = {}

        # 构建VALUES子句
        values_parts = []
        for idx, data in enumerate(data_list):
            placeholders = []
            for col in columns:
                param_name = f"{col}_{idx}"
                placeholders.append(f":{param_name}")
                params[param_name] = data.get(col)
            values_parts.append(f"({', '.join(placeholders)})")

        # 构建UPDATE语句
        set_parts = [f"{col} = data.{col}" for col in columns if col not in key_columns]
        join_parts = [f"t.{kc} = data.{kc}" for kc in key_columns]

        sql = f"""UPDATE {table.name} t
SET {', '.join(set_parts)}
FROM (VALUES {', '.join(values_parts)}) AS data ({', '.join(columns)})
WHERE {' AND '.join(join_parts)}"""

        return SQLResult(sql=sql, params=params)

    def build_delete(self, table: Table, conditions: Dict[str, Any]) -> SQLResult:
        where_parts = [f"{k} = :{k}" for k in conditions.keys()]
        sql = f"DELETE FROM {table.name} WHERE {' AND '.join(where_parts)}"
        return SQLResult(sql=sql, params=conditions)


class SQLBuilderFactory:
    """SQL构建器工厂"""

    _builders = {
        'mysql': MySQLBuilder,
        'postgresql': PostgreSQLBuilder,
        'sqlite': PostgreSQLBuilder,
    }

    @classmethod
    def get_builder(cls, dialect: str) -> SQLBuilder:
        """获取对应数据库的构建器"""
        builder_class = cls._builders.get(dialect.lower())
        if not builder_class:
            raise ValueError(f"Unsupported database dialect: {dialect}")
        return builder_class()

    @classmethod
    def register_builder(cls, dialect: str, builder_class: type):
        """注册新的构建器"""
        if not issubclass(builder_class, SQLBuilder):
            raise TypeError(f"{builder_class} must inherit from SQLBuilder")
        cls._builders[dialect.lower()] = builder_class