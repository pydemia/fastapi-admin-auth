from typing import Any
from fastapi import Depends
# from .crud import (
#     get_courses_all,
#     get_courses_by_ids,
#     get_courses_by_range,
#     get_course_by_id,
#     create_course,
#     update_course,
#     delete_course,
# )

# get_courses_all
# get_courses_by_ids
# get_courses_by_range
# get_course_by_id
# create_course
# update_course
# delete_course
from mainapp.core.types.exceptions import HandledException, ResponseCode
from .models import Course, Certificate
from .crud import CourseCRUD, CertificateCRUD
from .schema import UpdateCourseRequest, CertificateRequest

from ..student.crud import StudentCRUD


class CourseService:
    def __init__(self):
        pass

    def __call__(
        self,
        course_crud: CourseCRUD = Depends(CourseCRUD()),
        cert_crud: CertificateCRUD = Depends(CertificateCRUD()),
        student_crud: StudentCRUD = Depends(StudentCRUD()),
    ):
        self.course_crud = course_crud
        self.cert_crud = cert_crud
        self.student_crud = student_crud
        return self


    def add_new_course(
        self,
        course: dict[str, Any] | Course,
    ) -> Course:
        if isinstance(course, dict):
            course = Course(
                name=course["name"],
                description=course.get("description"),
                book_id=course.get("book_id"),
                certificate_id=course.get("certificate_id"),
            )
        course = self.course_crud.create(course)
        return course


    def add_new_courses(
        self,
        course_list: list[dict[str, Any] | Course],
    ) -> list[Course]:
        courses = [self.add_new_course(course) for course in course_list]
        return courses


    def get_course(
        self,
        id_or_name_or_entity: int | str | Course,
    ) -> Course | None:
        if isinstance(id_or_name_or_entity, int):
            course = self.course_crud.get_by_id(id_or_name_or_entity)
        elif isinstance(id_or_name_or_entity, str):
            course = self.course_crud.get_by_name(id_or_name_or_entity)
        elif isinstance(id_or_name_or_entity, Course):
            course = self.course_crud.get_by_id(id_or_name_or_entity.id)
        else:
            raise HandledException(ResponseCode.ENTITY_ID_INVALID)

        return course


    def get_courses_all(
        self,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Course]:
        if page:
            courses = self.course_crud.get_by_range(page=1)
        else:
            courses = self.course_crud.get_all()
        return [c for c in courses if c is not None]
    
    def update_course_description(
        self,
        name: str,
        description: str,
    ) -> Course:
        course = self.get_course(name)
        if not course:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)
        
        course.description = description
        course = self.course_crud.update(course)
        return course


    def update_course(
        self,
        course_id: int,
        new_course: Course | UpdateCourseRequest,
    ) -> Course:
        
        old_course: Course | None = self.course_crud.get_by_id(course_id)
        if not old_course:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)


        old_course.name = new_course.name
        old_course.description = new_course.description
        if isinstance(new_course, Course):
            if new_course.id is not None and old_course.id != new_course.id:
                raise HandledException(ResponseCode.ENTITY_NOT_FOUND)
        
            for f in new_course.model_fields:
                setattr(old_course, f, getattr(new_course, f))

        elif isinstance(new_course, UpdateCourseRequest):
            for f in new_course.model_fields:
                if f in ("certificate", "students"):
                    pass
                else:
                    setattr(old_course, f, getattr(new_course, f))

            if new_course.certificate_id is not None:
                old_course.certificate = self.get_certificate(new_course.certificate_id)

            if new_course.students:
                old_course.students = self.student_crud.get_by_ids(new_course.students)

        course = self.course_crud.update(old_course)

        return course


    def delete_course(
        self,
        id_or_name: str,
    ) -> bool:
        course = self.get_course(id_or_name)
        if not course:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)

        return self.course_crud.delete(course)


    def get_certificate(
        self,
        id_or_name_or_entity: int | str | Certificate,
    ) -> Certificate | None:
        if isinstance(id_or_name_or_entity, int):
            certificate = self.cert_crud.get_by_id(id_or_name_or_entity)
        elif isinstance(id_or_name_or_entity, str):
            certificate = self.cert_crud.get_by_name(id_or_name_or_entity)
        elif isinstance(id_or_name_or_entity, Course):
            certificate = self.cert_crud.get_by_id(id_or_name_or_entity.id)
        else:
            raise HandledException(ResponseCode.ENTITY_ID_INVALID)

        return certificate


    def update_certificate(
        self,
        cert_id: int,
        new_cert: Certificate | CertificateRequest,
    ) -> Certificate:
        

        old_cert: Certificate | None = self.cert_crud.get_by_id(cert_id)
        if not old_cert:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)


        old_cert.name = new_cert.name
        old_cert.description = new_cert.description
        if isinstance(new_cert, Certificate):
            if old_cert.id != new_cert.id:
                raise HandledException(ResponseCode.ENTITY_NOT_FOUND)

        # elif isinstance(new_cert, CertificateRequest):
        #     if new_cert.course_id is not None:
        #         old_cert.course_id = new_cert.course_id
        #         old_cert.course = Course.model_validate(old_cert.course.model_dump())

        certificate = self.course_crud.update(old_cert)

        return certificate


    def delete_certificate(
        self,
        cert_id: str,
    ) -> bool:
        certificate = self.get_certificate(cert_id)
        if not certificate:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)

        return self.crud.delete(certificate)
