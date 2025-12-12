from typing import Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy import delete, select, update
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.sql import ColumnElement

ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class BaseMapper(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        assert issubclass(model, DeclarativeBase), "必须是 s.o.DeclarativeBase 的子类"
        assert hasattr(model, "id"), "必须有id"
        assert hasattr(model, "is_delete"), "必须有软删除字段"
        self.model: Type[ModelType] = model

    def select_by_id(self, session: Session, id: int) -> Union[ModelType, None]:
        """获取单个对象 by id"""
        return session.get(self.model, id)

    def select_by_condition(
        self, session: Session, condition: ColumnElement[bool]
    ) -> Union[ModelType, None]:
        """获取单个对象 by 条件(自动过滤软删除)"""
        stmt = select(self.model).where(self._not_soft_del).where(condition).limit(1)
        return session.scalars(stmt).first()

    def select_list(
        self,
        session: Session,
        condition: Optional[ColumnElement[bool]] = None,
        limit: Optional[int] = None,
    ) -> List[ModelType]:
        """批量获取"""
        stmt = select(self.model).where(self._not_soft_del)
        if condition:
            stmt = stmt.where(condition)
        if limit:
            stmt = stmt.limit(limit)
        return session.scalars(stmt).all()

    def insert(self, session: Session, po: ModelType) -> ModelType:
        """插入"""
        session.add(po)
        return po

    def insert_list(
        self, session: Session, po_list: List[ModelType]
    ) -> List[ModelType]:
        """批量插入"""
        for po in po_list:
            session.add(po)
        return po_list

    def update_by_po(self, session: Session, po: ModelType) -> ModelType:
        return session.merge(po)

    def update_by_id(self, session: Session, id: int, values: dict):
        stmt = update(self.model).where(self.model.id == id).values(**values)
        res = session.execute(stmt)
        return res.rowcount or 0

    def update_by_condition(
        self, session: Session, values: dict, condition: ColumnElement[bool]
    ) -> int:
        stmt = update(self.model).values(**values)
        if condition is not None:
            stmt = stmt.where(condition)
        res = session.execute(stmt)
        return res.rowcount or 0

    def upsert_by(self, session: Session, unique_field: str, po: ModelType):
        unique_value = getattr(po, unique_field)
        stmt = select(self.model).where(
            getattr(self.model, unique_field) == unique_value
        )
        existed = session.scalars(stmt).first()

        if existed:
            po.id = existed.id
            self.update_by_po(session, po)
            return po

        session.add(po)
        return po

    def delete_soft_by_condition(
        self, session: Session, condition: ColumnElement[bool]
    ) -> int:
        """软删除 by id"""
        return self.update_by_condition(session, {"is_delete": True}, condition)

    def delete_soft(self, session: Session, id: int) -> int:
        """软删除 by id"""
        return self.update_by_id(session, id, {"is_delete": True})

    def delete_by_condition(
        self, session: Session, condition: ColumnElement[bool]
    ) -> int:
        """硬删除 by id"""
        stmt = delete(self.model).where(condition)
        res = session.execute(stmt)
        return res.rowcount or 0

    def delete(self, session: Session, id: int) -> int:
        """硬删除 by id"""
        stmt = delete(self.model).where(self.model.id == id)
        res = session.execute(stmt)
        return res.rowcount or 0

    @property
    def _not_soft_del(self) -> ColumnElement[bool]:
        return self.model.is_delete.is_(False)
