# xll_kit/services/mixins/sort_mixin.py
from sqlalchemy import asc, desc
from typing import List

class SortMixin:
    def sortable_fields(self):
        return []

    def apply_sort(self, stmt, sort: str = None):
        if not sort:
            return stmt
        sort_items = [s.strip() for s in sort.split(",") if s.strip()]
        clauses = []
        for s in sort_items:
            direction = desc if s.startswith("-") else asc
            name = s.lstrip("-")
            if name in self.sortable_fields():
                clauses.append(direction(getattr(self.crud.model, name)))
        if clauses:
            stmt = stmt.order_by(*clauses)
        return stmt
