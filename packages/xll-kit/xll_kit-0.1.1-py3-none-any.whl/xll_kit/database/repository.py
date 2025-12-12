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

    def __init__(self, model: Type[ModelType], session: Session):
        """
        初始化 Repository

        Args:
            model: SQLAlchemy Model 类
            session: 数据库 Session
        """
        self.model = model
        self.session = session

    def get(self, id: int) -> Optional[ModelType]:
        """
        根据 ID 获取单条记录

        Args:
            id: 记录 ID

        Returns:
            Model 实例或 None
        """
        return self.session.get(self.model, id)

    def get_by(self, **filters) -> Optional[ModelType]:
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
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[ModelType]:
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

        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def filter(self, **filters) -> List[ModelType]:
        """
        根据条件过滤

        Args:
            **filters: 过滤条件

        Returns:
            Model 实例列表
        """
        stmt = select(self.model).filter_by(**filters)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def create(self, data: Dict[str, Any]) -> ModelType:
        """
        创建新记录

        Args:
            data: 数据字典

        Returns:
            创建的 Model 实例
        """
        instance = self.model(**data)
        self.session.add(instance)
        self.session.flush()  # 获取 ID
        return instance

    def create_many(self, data_list: List[Dict[str, Any]]) -> List[ModelType]:
        """
        批量创建

        Args:
            data_list: 数据字典列表

        Returns:
            创建的 Model 实例列表
        """
        instances = [self.model(**data) for data in data_list]
        self.session.add_all(instances)
        self.session.flush()
        return instances

    def update(self, id: int, data: Dict[str, Any]) -> Optional[ModelType]:
        """
        更新记录

        Args:
            id: 记录 ID
            data: 更新数据

        Returns:
            更新后的 Model 实例或 None
        """
        instance = self.get(id)
        if instance:
            for key, value in data.items():
                setattr(instance, key, value)
            self.session.flush()
        return instance

    def update_by(self, filters: Dict[str, Any], data: Dict[str, Any]) -> int:
        """
        根据条件批量更新

        Args:
            filters: 过滤条件
            data: 更新数据

        Returns:
            影响的行数
        """
        stmt = update(self.model).filter_by(**filters).values(**data)
        result = self.session.execute(stmt)
        return result.rowcount

    def delete(self, id: int) -> bool:
        """
        删除记录

        Args:
            id: 记录 ID

        Returns:
            是否删除成功
        """
        instance = self.get(id)
        if instance:
            self.session.delete(instance)
            self.session.flush()
            return True
        return False

    def delete_by(self, **filters) -> int:
        """
        根据条件批量删除

        Args:
            **filters: 过滤条件

        Returns:
            删除的行数
        """
        stmt = delete(self.model).filter_by(**filters)
        result = self.session.execute(stmt)
        return result.rowcount

    def count(self, **filters) -> int:
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

        result = self.session.execute(stmt)
        return result.scalar()

    def exists(self, **filters) -> bool:
        """
        判断记录是否存在

        Args:
            **filters: 过滤条件

        Returns:
            是否存在
        """
        return self.count(**filters) > 0

    def paginate(
            self,
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
        total = self.count(**filters)

        stmt = select(self.model)
        if filters:
            stmt = stmt.filter_by(**filters)

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = self.session.execute(stmt)
        items = list(result.scalars().all())

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    def commit(self):
        """提交事务"""
        self.session.commit()

    def rollback(self):
        """回滚事务"""
        self.session.rollback()

    def refresh(self, instance: ModelType):
        """刷新实例"""
        self.session.refresh(instance)