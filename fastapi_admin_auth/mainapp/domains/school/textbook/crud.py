from typing import Iterable
from fastapi import Depends
from sqlmodel import select, col
from mainapp.core.database import db, Session, get_pk_values

from mainapp.core.types.exceptions import HandledException, ResponseCode
from .models import Textbook


class TextbookCRUD:
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
    ) -> list[Textbook | None]:    

        session = self.session
        stmt = select(Textbook)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_by_range(
        self,
        page: int = 0,
        page_size: int = 10,
        order_by_asc: bool = True,
    ) -> list[Textbook | None]:

        session = self.session
        stmt = select(Textbook)
        if order_by_asc:
            stmt.order_by(col(Textbook.id).asc())
        else:
            stmt.order_by(col(Textbook.id).desc())
        stmt = stmt.offset(page_size * page)
        stmt = stmt.limit(page_size)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_by_ids(
        self,
        ids: Iterable,
    ) -> list[Textbook | None]:

        session = self.session
        stmt = select(Textbook).where(Textbook.id in ids)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_by_model(
        self,
        record: Textbook,
    ) -> Textbook | None:

        session = self.session
        
        record = session.get_one(Textbook, get_pk_values(record))
        # stmt = session.exec(stmt)
        # return stmt.first()
        return record


    def get_by_id(
        self,
        *pk,
    ) -> Textbook | None:

        session = self.session
        return session.get_one(Textbook, pk)

    def get_by_name(
        self,
        name: str,
    ) -> Textbook | None:

        session = self.session
        stmt = select(Textbook).where(Textbook.name == name)
        stmt = session.exec(stmt)
        return stmt.first()

    def create(
        self,
        record: Textbook,
    ) -> Textbook:

        session = self.session
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


    def get_or_create(
        self,
        record: Textbook,
    ) -> Textbook:

        if record.id:
            old: Textbook | None = self.get_by_model(record)
        
        if old:
            return old
        else:
            return self.create(record)


    def update(
        self,
        record: Textbook,
    ) -> Textbook:

        session = self.session
        old = session.get(Textbook, record.id)
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
        record: Textbook,
    ) -> bool:
        if self.get_by_model(record):
            session = self.session
            session.delete(record)
            session.commit()
            return True
        else:
            return False
