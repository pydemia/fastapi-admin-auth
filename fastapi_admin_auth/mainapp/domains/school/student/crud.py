from typing import Iterable
from fastapi import Depends
from sqlmodel import select, col, and_
from mainapp.core.database import db, Session

from .models import Student


class StudentCRUD:
    def __init__(self):
        pass

    def __call__(
        self,
        session: Session = Depends(db.get_session),
    ):
        self.session = session
        return self

    def get_students_all(
        self,
    ) -> list[Student | None]:    

        session = self.session
        stmt = select(Student)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_students_by_range(
        self,
        page: int = 0,
        page_size: int = 10,
        order_by_asc: bool = True,
    ) -> list[Student | None]:

        session = self.session
        stmt = select(Student)
        if order_by_asc:
            stmt.order_by(col(Student.id).asc())
        else:
            stmt.order_by(col(Student.id).desc())
        stmt = stmt.offset(page_size * page)
        stmt = stmt.limit(page_size)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_students_by_ids(
        self,
        ids: Iterable,
    ) -> list[Student | None]:

        session = self.session
        stmt = select(Student).where(Student.id in ids)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_student_by_id(
        self,
        id,
    ) -> Student | None:

        session = self.session
        stmt = select(Student).where(Student.id == id)
        stmt = session.exec(stmt)
        return stmt.first()

    def get_student_by_name(
        self,
        firstname: str,
        lastname: str,
    ) -> Student | None:

        session = self.session
        stmt = select(Student).where(
            and_(Student.firstname == firstname, Student.lastname == lastname)
        )
        stmt = session.exec(stmt)
        return stmt.first()

    def create_student(
        self,
        student: Student,
    ) -> Student:

        session = self.session
        session.add(student)
        session.commit()
        session.refresh(student)
        return student


    def get_or_create_student(
        self,
        firstname: str,
        lastname: str,
    ) -> Student:
        student: Student | None = self.get_student_by_name(
            firstname=firstname,
            lastname=lastname,
        )
        if student:
            return student
        else:
            student = Student(firstname=firstname, lastname=lastname)
            student = self.create_student(student)
            return student


    def update_student(
        self,
        student: Student,
    ) -> Student:

        session = self.session
        session.add(student)
        session.commit()
        session.refresh(student)
        return student

    def delete_student(
        self,
        student: Student,
    ) -> None:
        session = self.session
        session.delete(student)
        session.commit()
