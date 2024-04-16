# _*_ coding: utf-8 _*_
"""
"""
from datetime import datetime
from typing import Callable, ContextManager, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import false, true
from autologging import logged
from ..models import ModelList
from mainapp.core.types.exceptions import HandledException, ResponseCode

__all__ = [
    "ItemRepository"
]


@logged
class ItemListRepository:
    """
    """
    def __init__(self, session_factory: Callable[..., ContextManager[Session]]) -> None:
        """
        """
        self.session_factory = session_factory

    def get_all(self, order_by_asc=True) -> Optional[list]:
        """
        """
        with self.session_factory() as session:
            stmt = session.query(ModelList)
            stmt = stmt.filter(ModelList.delete_yn == false())

            if order_by_asc is True:
                stmt = stmt.order_by(ModelList.update_dt.asc())
            else:
                stmt = stmt.order_by(ModelList.update_dt.desc())

            return stmt.all()

    def get_by_range(self, page: int = 0, page_size: int = 10, order_by_asc=True) -> Optional[list]:
        """
        """
        with self.session_factory() as session:
            stmt = session.query(ModelList)
            stmt = stmt.filter(ModelList.delete_yn == false())

            if order_by_asc is True:
                stmt = stmt.order_by(ModelList.update_dt.asc())
            else:
                stmt = stmt.order_by(ModelList.update_dt.desc())

            stmt = stmt.limit(page_size)
            stmt = stmt.offset(page * page_size)

            return stmt.all()

    def get_by_id(self, model_id: str, project_id: int, workflow_id: int) -> Optional[ModelList]:
        """
        """
        with self.session_factory() as session:
            stmt = session.query(ModelList)
            stmt = stmt.filter(ModelList.model_id == model_id)
            stmt = stmt.filter(ModelList.project_id == project_id)
            stmt = stmt.filter(ModelList.workflow_id == workflow_id)
            stmt = stmt.filter(ModelList.delete_yn == false())
            row = stmt.first()

            if not row:
                raise HandledException(ResponseCode.MODEL_NOT_EXISTS, e=None)

            return row

    def add(self, record: ModelList) -> ModelList:
        """
        """
        with self.session_factory() as session:
            if not record.create_dt:
                record.create_dt = datetime.now()

            session.add(record)
            session.commit()

            return session.refresh(record)

    def update(self, record: ModelList) -> None:
        """
        """
        with self.session_factory() as session:
            if not record.update_dt:
                record.update_dt = datetime.now()

            session.merge(record)
            session.commit()

    def delete_by_id(self, model_id: str, project_id: int, workflow_id: int) -> None:
        """
        """
        with self.session_factory() as session:
            stmt = session.query(ModelList)
            stmt = stmt.filter(ModelList.model_id == model_id)
            stmt = stmt.filter(ModelList.project_id == project_id)
            stmt = stmt.filter(ModelList.workflow_id == workflow_id)
            stmt = stmt.filter(ModelList.delete_yn == false())
            row = stmt.first()

            if row:
                row.delete_yn = true()
                row.delete_dt = datetime.now()
                session.commit()
            else:
                raise HandledException(ResponseCode.MODEL_NOT_EXISTS)
