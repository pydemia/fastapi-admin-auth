from typing import Iterable
from fastapi import Depends
from sqlmodel import select, col
from mainapp.core.database import db, Session, get_pk_values

from mainapp.core.types.exceptions import HandledException, ResponseCode
from .models import Course, Certificate


class CourseCRUD:
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
    ) -> list[Course | None]:    

        session = self.session
        stmt = select(Course)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_by_range(
        self,
        page: int = 0,
        page_size: int = 10,
        order_by_asc: bool = True,
    ) -> list[Course | None]:

        session = self.session
        stmt = select(Course)
        if order_by_asc:
            stmt.order_by(col(Course.id).asc())
        else:
            stmt.order_by(col(Course.id).desc())
        stmt = stmt.offset(page_size * page)
        stmt = stmt.limit(page_size)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_by_ids(
        self,
        ids: Iterable,
    ) -> list[Course | None]:

        session = self.session
        stmt = select(Course).where(Course.id in ids)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_by_model(
        self,
        record: Course,
    ) -> Course | None:

        session = self.session
        
        record = session.get_one(Course, get_pk_values(record))
        # stmt = session.exec(stmt)
        # return stmt.first()
        return record


    def get_by_id(
        self,
        *pk,
    ) -> Course | None:

        session = self.session
        return session.get_one(Course, pk)

    def get_by_name(
        self,
        name: str,
    ) -> Course | None:

        session = self.session
        stmt = select(Course).where(Course.name == name)
        stmt = session.exec(stmt)
        return stmt.first()

    def create(
        self,
        record: Course,
    ) -> Course:

        session = self.session
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


    def get_or_create(
        self,
        record: Course,
    ) -> Course:

        if record.id:
            old: Course | None = self.get_by_model(record)
        
        if old:
            return old
        else:
            return self.create(record)


    def update(
        self,
        record: Course,
    ) -> Course:

        session = self.session
        old = session.get(Course, record.id)
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
        record: Course,
    ) -> bool:
        if self.get_by_model(record):
            session = self.session
            session.delete(record)
            session.commit()
            return True
        else:
            return False


class CertificateCRUD:
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
    ) -> list[Certificate | None]:    

        session = self.session
        stmt = select(Certificate)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_by_range(
        self,
        page: int = 0,
        page_size: int = 10,
        order_by_asc: bool = True,
    ) -> list[Certificate | None]:

        session = self.session
        stmt = select(Certificate)
        if order_by_asc:
            stmt.order_by(col(Certificate.id).asc())
        else:
            stmt.order_by(col(Certificate.id).desc())
        stmt = stmt.offset(page_size * page)
        stmt = stmt.limit(page_size)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_by_ids(
        self,
        ids: Iterable,
    ) -> list[Certificate | None]:

        session = self.session
        stmt = select(Certificate).where(Certificate.id in ids)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_by_model(
        self,
        record: Certificate,
    ) -> Certificate | None:

        session = self.session
        
        record = session.get_one(Certificate, get_pk_values(record))
        # stmt = session.exec(stmt)
        # return stmt.first()
        return record


    def get_by_id(
        self,
        *pk,
    ) -> Certificate | None:

        session = self.session
        return session.get_one(Certificate, pk)

    def get_by_name(
        self,
        name: str,
    ) -> Certificate | None:

        session = self.session
        stmt = select(Certificate).where(Certificate.name == name)
        stmt = session.exec(stmt)
        return stmt.first()

    def create(
        self,
        record: Certificate,
    ) -> Certificate:

        session = self.session
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


    def get_or_create(
        self,
        record: Certificate,
    ) -> Certificate:

        if record.id:
            old: Certificate | None = self.get_by_model(record)
        
        if old:
            return old
        else:
            return self.create(record)


    def update(
        self,
        record: Certificate,
    ) -> Certificate:

        session = self.session
        old = session.get(Certificate, record.id)
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
        record: Certificate,
    ) -> bool:
        if self.get_by_model(record):
            session = self.session
            session.delete(record)
            session.commit()
            return True
        else:
            return False
