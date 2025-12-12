# xll_kit/cruds/mixins/upsert_mixin.py
from typing import List, Dict, Any

class UpsertMixin:
    def batch_upsert(self, session, data_list: List[Dict[str, Any]], unique_keys: List[str]):
        """
        占位实现：子类实现具体 DB upsert（Postgres ON CONFLICT 或 MySQL REPLACE/INSERT...）
        """
        raise NotImplementedError("batch_upsert must be implemented in DB-specific subclass")
