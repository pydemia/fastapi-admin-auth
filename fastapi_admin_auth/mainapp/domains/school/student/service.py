from typing import Any
from fastapi import Depends
# from .crud import (
#     get_students_all,
#     get_students_by_ids,
#     get_students_by_range,
#     get_student_by_id,
#     create_student,
#     update_student,
#     delete_student,
# )

# get_students_all
# get_students_by_ids
# get_students_by_range
# get_student_by_id
# create_student
# update_student
# delete_student
from mainapp.core.types.exceptions import HandledException, ResponseCode
from .models import Student
from .crud import StudentCRUD


class StudentService:
    def __init__(self):
        pass

    def __call__(
        self,
        crud: StudentCRUD = Depends(StudentCRUD()),
    ):
        self.student_crud = crud
        return self


    def add_new_student(
        self,
        student: dict[str, Any] | Student,
    ) -> Student:
        if isinstance(student, dict):
            student = Student(
                firstname=student["firstname"],
                lastname=student["lastname"],
                description=student.get("description"),
            )
        student = self.student_crud.create(student)
        return student


    def add_new_students(
        self,
        student_list: list[dict[str, Any] | Student],
    ) -> list[Student]:
        students = [self.add_new_student(student) for student in student_list]
        return students


    def get_student_by_name(
        self,
        firstname: str,
        lastname: str,
    ) -> Student | None:
        student = self.textbook_crud.get_by_name(firstname, lastname)
        return student


    def get_student_by_id_or_entity(
        self,
        id_or_entity: int | Student,
    ) -> Student | None:
        if isinstance(id_or_entity, int):
            student = self.textbook_crud.get_by_id(id_or_entity)
        elif isinstance(id_or_entity, Student):
            student = self.textbook_crud.get_by_id(id_or_entity.id)
        else:
            raise HandledException(ResponseCode.ENTITY_ID_INVALID)

        return student


    def get_students_all(
        self,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Student | None]:
        if page:
            students = self.textbook_crud.get_by_range(page=1)
        else:
            students = self.textbook_crud.get_all()
        return students
    
    def update_student_description(
        self,
        name: str,
        description: str,
    ) -> Student:
        student = self.get_student(name)
        if not student:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)
        
        student.description = description
        student = self.student_crud.update(student)
        return student


    def update_student(
        self,
        student_id: int,
        new_student: Student,
    ) -> Student:
        old_student: Student | None = self.textbook_crud.get_by_id(student_id)
        if not old_student:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)

        old_student.firstname = new_student.firstname
        old_student.lastname = new_student.lastname
        old_student.description = new_student.description
        student = self.student_crud.update(old_student)

        return student


    def delete_student(
        self,
        student_id: str,
    ) -> bool:
        student = self.get_student_by_id_or_entity(student_id)
        if not student:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)

        return self.student_crud.delete(student)
