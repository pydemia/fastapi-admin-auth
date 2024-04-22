from typing import Iterable
from fastapi import Depends
from sqlmodel import select, col
from mainapp.core.database import db, Session

from .models import Course


class CourseCRUD:
    def __init__(self):
        pass

    def __call__(
        self,
        session: Session = Depends(db.get_session),
    ):
        self.session = session
        return self

    def get_courses_all(
        self,
    ) -> list[Course | None]:    

        session = self.session
        stmt = select(Course)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_courses_by_range(
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


    def get_courses_by_ids(
        self,
        ids: Iterable,
    ) -> list[Course | None]:

        session = self.session
        stmt = select(Course).where(Course.id in ids)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_course_by_id(
        self,
        id,
    ) -> Course | None:

        session = self.session
        stmt = select(Course).where(Course.id == id)
        stmt = session.exec(stmt)
        return stmt.first()

    def get_course_by_name(
        self,
        name: str,
    ) -> Course | None:

        session = self.session
        stmt = select(Course).where(Course.name == name)
        stmt = session.exec(stmt)
        return stmt.first()

    def create_course(
        self,
        course: Course,
    ) -> Course:

        session = self.session
        session.add(course)
        session.commit()
        session.refresh(course)
        return course


    def get_or_create_course(
        self,
        name: str,
    ) -> Course:
        course: Course | None = self.get_course_by_name(
            name=name
        )
        if course:
            return course
        else:
            course = Course(name=name)
            course = self.create_course(course)
            return course


    def update_course(
        self,
        course: Course,
    ) -> Course:

        session = self.session
        session.add(course)
        session.commit()
        session.refresh(course)
        return course

    def delete_course(
        self,
        course: Course,
    ) -> None:
        session = self.session
        session.delete(course)
        session.commit()
