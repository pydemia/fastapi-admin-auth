from typing import Iterable
from fastapi import Depends
from sqlmodel import select, col, and_
from mainapp.core.database import db, Session

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

    def get_teachers_all(
        self,
    ) -> list[Teacher | None]:    

        session = self.session
        stmt = select(Teacher)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_teachers_by_range(
        self,
        page: int = 0,
        page_size: int = 10,
        order_by_asc: bool = True,
    ) -> list[Teacher | None]:

        session = self.session
        stmt = select(Teacher)
        if order_by_asc:
            stmt.order_by(col(Teacher.id).asc())
        else:
            stmt.order_by(col(Teacher.id).desc())
        stmt = stmt.offset(page_size * page)
        stmt = stmt.limit(page_size)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_teachers_by_ids(
        self,
        ids: Iterable,
    ) -> list[Teacher | None]:

        session = self.session
        stmt = select(Teacher).where(Teacher.id in ids)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_teacher_by_id(
        self,
        id,
    ) -> Teacher | None:

        session = self.session
        stmt = select(Teacher).where(Teacher.id == id)
        stmt = session.exec(stmt)
        return stmt.first()

    def get_teacher_by_name(
        self,
        firstname: str,
        lastname: str,
    ) -> Teacher | None:

        session = self.session
        stmt = select(Teacher).where(
            and_(Teacher.firstname == firstname, Teacher.lastname == lastname)
        )
        stmt = session.exec(stmt)
        return stmt.first()

    def create_teacher(
        self,
        teacher: Teacher,
    ) -> Teacher:

        session = self.session
        session.add(teacher)
        session.commit()
        session.refresh(teacher)
        return teacher


    def get_or_create_teacher(
        self,
        firstname: str,
        lastname: str,
    ) -> Teacher:
        teacher: Teacher | None = self.get_teacher_by_name(
            firstname=firstname,
            lastname=lastname,
        )
        if teacher:
            return teacher
        else:
            teacher = Teacher(firstname=firstname, lastname=lastname)
            teacher = self.create_teacher(teacher)
            return teacher


    def update_teacher(
        self,
        teacher: Teacher,
    ) -> Teacher:

        session = self.session
        session.add(teacher)
        session.commit()
        session.refresh(teacher)
        return teacher

    def delete_teacher(
        self,
        teacher: Teacher,
    ) -> None:
        session = self.session
        session.delete(teacher)
        session.commit()
