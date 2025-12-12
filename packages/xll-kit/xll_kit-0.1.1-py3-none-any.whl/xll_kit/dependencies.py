from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from .database.session_manager import get_session_manager


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库 Session（FastAPI 依赖注入）

    使用示例:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
    """
    session_manager = get_session_manager()

    session = session_manager.get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# 便捷的类型别名
DBSession = Depends(get_db)
