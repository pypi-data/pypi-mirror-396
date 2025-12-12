# xll_kit/services/mixins/pagination_mixin.py
from xll_kit.services.pagination import PaginationResult
from sqlalchemy import select, func

class PaginationMixin:
    def paginate(self, session, stmt, skip: int, limit: int) -> PaginationResult:
        total_stmt = select(func.count()).select_from(stmt.subquery())
        total = session.scalar(total_stmt) or 0
        items = session.execute(stmt.offset(skip).limit(limit)).scalars().all()
        return PaginationResult(items=items, total=total, page=skip // limit + 1, limit=limit)
