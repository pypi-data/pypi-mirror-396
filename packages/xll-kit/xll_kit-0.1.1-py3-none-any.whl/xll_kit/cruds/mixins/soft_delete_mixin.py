# xll_kit/cruds/mixins/soft_delete_mixin.py
from datetime import datetime

class SoftDeleteMixin:
    def soft_delete(self, session, db_obj):
        if hasattr(db_obj, "deleted_at"):
            setattr(db_obj, "deleted_at", datetime.now())
            session.add(db_obj)
            session.flush()
            return db_obj
        else:
            session.delete(db_obj)
            session.flush()
            return None
