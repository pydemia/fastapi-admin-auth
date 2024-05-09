from typing import Iterable
from fastapi import Depends
from sqlmodel import select, col
from mainapp.core.database import db, Session, get_pk_values

from mainapp.core.types.exceptions import HandledException, ResponseCode
from .models import Teacher


class TeacherCRUD:
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
    ) -> list[Teacher | None]:    

        with self.session as session:
            stmt = select(Teacher)
            stmt = session.exec(stmt)
            return stmt.all()


    def get_by_range(
        self,
        page: int = 0,
        page_size: int = 10,
        order_by_asc: bool = True,
    ) -> list[Teacher | None]:

        with self.session as session:
            stmt = select(Teacher)
            if order_by_asc:
                stmt.order_by(col(Teacher.id).asc())
            else:
                stmt.order_by(col(Teacher.id).desc())
            stmt = stmt.offset(page_size * page)
            stmt = stmt.limit(page_size)
            stmt = session.exec(stmt)
            return stmt.all()


    def get_by_ids(
        self,
        ids: Iterable,
    ) -> list[Teacher | None]:

        with self.session as session:
            stmt = select(Teacher).where(Teacher.id in ids)
            stmt = session.exec(stmt)
            return stmt.all()


    def get_by_model(
        self,
        record: Teacher,
    ) -> Teacher | None:

        with self.session as session:
            record = session.get_one(Teacher, get_pk_values(record))
            # stmt = session.exec(stmt)
            # return stmt.first()
            return record


    def get_by_id(
        self,
        *pk,
    ) -> Teacher | None:

        with self.session as session:
            return session.get_one(Teacher, pk)

    def get_by_name(
        self,
        firstname: str,
        lastname: str,
    ) -> Teacher | None:

        with self.session as session:
            stmt = select(Teacher).where(
                col(Teacher.firstname) == firstname,
                col(Teacher.lastname) == lastname,
            )
            stmt = session.exec(stmt)
            return stmt.first()

    def create(
        self,
        record: Teacher,
    ) -> Teacher:

        with self.session as session:
            session.add(record)
            session.commit()
            session.refresh(record)
            return record


    def get_or_create(
        self,
        record: Teacher,
    ) -> Teacher:

        if record.id:
            old: Teacher | None = self.get_by_model(record)
        
        if old:
            return old
        else:
            return self.create(record)


    def update(
        self,
        record: Teacher,
    ) -> Teacher:

        with self.session as session:
            old = session.get(Teacher, record.id)
            if old:
                dumped = record.model_dump(exclude_unset=True)
                old.sqlmodel_update(dumped)
                session.add(old)
                session.commit()
                session.refresh(old)
            else:
                raise HandledException(ResponseCode.ENTITY_NOT_FOUND)
            return old

    def delete(
        self,
        record: Teacher,
    ) -> bool:
        if self.get_by_model(record):
            with self.session as session:
                session.delete(record)
                session.commit()
                return True
        else:
            return False
