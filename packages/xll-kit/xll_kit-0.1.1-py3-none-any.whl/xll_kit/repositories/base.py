"""
Repository 模式实现
提供通用的 CRUD 操作
"""
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, func

from xll_kit.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    基础 Repository 类
    提供通用的 CRUD 操作

    使用示例:
        class UserRepository(BaseRepository[User]):
            pass

        user_repo = UserRepository(User, session)
        user = user_repo.get(1)
    """

    def __init__(self, model: Type[ModelType]):
        """
        初始化 Repository

        Args:
            model: SQLAlchemy Model 类
        """
        self.model = model

    def get(self, session: Session, id: int) -> Optional[ModelType]:
        """
        根据 ID 获取单条记录

        Args:
            id: 记录 ID

        Returns:
            Model 实例或 None
        """
        return session.get(self.model, id)

    def get_by(self, session: Session, **filters) -> Optional[ModelType]:
        """
        根据条件获取单条记录

        Args:
            **filters: 过滤条件

        Returns:
            Model 实例或 None

        Example:
            user = repo.get_by(email='test@example.com')
        """
        stmt = select(self.model).filter_by(**filters)
        result = session.execute(stmt)
        return result.scalar_one_or_none()

    def get_all(self, session: Session, limit: Optional[int] = None, offset: int = 0) -> List[ModelType]:
        """
        获取所有记录

        Args:
            limit: 限制数量
            offset: 偏移量

        Returns:
            Model 实例列表
        """
        stmt = select(self.model).offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        result = session.execute(stmt)
        return list(result.scalars().all())

    def filter(self, session: Session, **filters) -> List[ModelType]:
        """
        根据条件过滤

        Args:
            **filters: 过滤条件

        Returns:
            Model 实例列表
        """
        stmt = select(self.model).filter_by(**filters)
        result = session.execute(stmt)
        return list(result.scalars().all())

    def create(self, session: Session, data: Dict[str, Any]) -> ModelType:
        """
        创建新记录

        Args:
            data: 数据字典

        Returns:
            创建的 Model 实例
        """
        instance = self.model(**data)
        session.add(instance)
        session.flush()  # 获取 ID
        return instance

    def create_many(self, session: Session, data_list: List[Dict[str, Any]]) -> List[ModelType]:
        """
        批量创建

        Args:
            data_list: 数据字典列表

        Returns:
            创建的 Model 实例列表
        """
        instances = [self.model(**data) for data in data_list]
        session.add_all(instances)
        session.flush()
        return instances

    def update(self, session: Session, id: int, data: Dict[str, Any]) -> Optional[ModelType]:
        """
        更新记录

        Args:
            id: 记录 ID
            data: 更新数据

        Returns:
            更新后的 Model 实例或 None
        """
        instance = self.get(session, id)
        if instance:
            for key, value in data.items():
                setattr(instance, key, value)
            session.flush()
        return instance

    def update_by(self, session: Session, filters: Dict[str, Any], data: Dict[str, Any]) -> int:
        """
        根据条件批量更新

        Args:
            filters: 过滤条件
            data: 更新数据

        Returns:
            影响的行数
        """
        stmt = update(self.model).filter_by(**filters).values(**data)
        result = session.execute(stmt)
        return result.rowcount

    def delete(self, session: Session, id: int) -> bool:
        """
        删除记录

        Args:
            id: 记录 ID

        Returns:
            是否删除成功
        """
        instance = self.get(id)
        if instance:
            session.delete(instance)
            session.flush()
            return True
        return False

    def delete_by(self, session: Session, **filters) -> int:
        """
        根据条件批量删除

        Args:
            **filters: 过滤条件

        Returns:
            删除的行数
        """
        stmt = delete(self.model).filter_by(**filters)
        result = session.execute(stmt)
        return result.rowcount

    def count(self, session: Session, **filters) -> int:
        """
        统计记录数

        Args:
            **filters: 过滤条件

        Returns:
            记录数量
        """
        stmt = select(func.count()).select_from(self.model)
        if filters:
            stmt = stmt.filter_by(**filters)

        result = session.execute(stmt)
        return result.scalar()

    def exists(self, session: Session, **filters) -> bool:
        """
        判断记录是否存在

        Args:
            **filters: 过滤条件

        Returns:
            是否存在
        """
        return self.count(session, **filters) > 0

    def paginate(
            self,
            session: Session,
            page: int = 1,
            page_size: int = 20,
            **filters
    ) -> Dict[str, Any]:
        """
        分页查询

        Args:
            page: 页码（从1开始）
            page_size: 每页数量
            **filters: 过滤条件

        Returns:
            包含数据和分页信息的字典
        """
        total = self.count(session, **filters)

        stmt = select(self.model)
        if filters:
            stmt = stmt.filter_by(**filters)

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = session.execute(stmt)
        items = list(result.scalars().all())

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    def commit(self, session: Session):
        """提交事务"""
        session.commit()

    def rollback(self, session: Session):
        """回滚事务"""
        session.rollback()

    def refresh(self, session: Session, instance: ModelType):
        """刷新实例"""
        session.refresh(instance)
