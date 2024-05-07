from typing import Iterable
from fastapi import Depends
from sqlmodel import select, col
from mainapp.core.database import db, Session
from mainapp.core.database import get_pk_values

from mainapp.core.types.exceptions import HandledException, ResponseCode
from .models import Item


class ItemCRUD:
    def __init__(self):
        pass

    def __call__(
        self,
        session: Session = Depends(db.get_session),
    ):
        self.session = session
        return self

    def get_all(
        self,
    ) -> list[Item | None]:    

        session = self.session
        stmt = select(Item)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_by_range(
        self,
        page: int = 0,
        page_size: int = 10,
        order_by_asc: bool = True,
    ) -> list[Item | None]:

        session = self.session
        stmt = select(Item)
        if order_by_asc:
            stmt.order_by(col(Item.id).asc())
        else:
            stmt.order_by(col(Item.id).desc())
        stmt = stmt.offset(page_size * page)
        stmt = stmt.limit(page_size)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_by_ids(
        self,
        ids: Iterable,
    ) -> list[Item | None]:

        session = self.session
        stmt = select(Item).where(Item.id in ids)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_by_model(
        self,
        record: Item,
    ) -> Item | None:

        session = self.session
        
        record = session.get_one(Item, get_pk_values(record))
        # stmt = session.exec(stmt)
        # return stmt.first()
        return record


    def get_by_id(
        self,
        *pk,
    ) -> Item | None:

        session = self.session
        return session.get_one(Item, pk)

    def get_by_name(
        self,
        name: str,
    ) -> Item | None:

        session = self.session
        stmt = select(Item).where(Item.name == name)
        stmt = session.exec(stmt)
        return stmt.first()

    def create(
        self,
        record: Item,
    ) -> Item:

        session = self.session
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


    def get_or_create(
        self,
        record: Item,
    ) -> Item:

        if record.id:
            old: Item | None = self.get_by_model(record)
        
        if old:
            return old
        else:
            return self.create(record)


    def update(
        self,
        record: Item,
    ) -> Item:

        session = self.session
        old = session.get(Item, record.id)
        if old:
            dumped = record.model_dump(exclude_unset=True)
            old.sqlmodel_update(dumped)
            session.add(record)
            session.commit()
            session.refresh(record)
        else:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)
        return record

    def delete(
        self,
        record: Item,
    ) -> bool:
        if self.get_by_model(record):
            session = self.session
            session.delete(record)
            session.commit()
            return True
        else:
            return False
