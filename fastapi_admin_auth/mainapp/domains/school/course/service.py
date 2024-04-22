from typing import Any
from .models import Course
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
from .crud import CourseCRUD


class CourseService:
    def __init__(self):
        pass

    def __call__(
        self,
        crud: CourseCRUD = Depends(CourseCRUD()),
    ):
        self.crud = crud
        return self


    def add_new_course(
        self,
        course: dict[str, Any] | Course,
    ) -> Course:
        if isinstance(course, dict):
            course = Course(
                name=course["name"],
                description=course.get("description"),
            )
        course = self.crud.create_course(course)
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
            course = self.crud.get_course_by_id(id_or_name_or_entity)
        elif isinstance(id_or_name_or_entity, str):
            course = self.crud.get_course_by_name(id_or_name_or_entity)
        elif isinstance(id_or_name_or_entity, Course):
            course = self.crud.get_course_by_id(id_or_name_or_entity.id)
        else:
            raise HandledException(ResponseCode.ENTITY_ID_INVALID)

        return course


    def get_courses_all(
        self,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Course | None]:
        if page:
            courses = self.crud.get_courses_by_range(page=1)
        else:
            courses = self.crud.get_courses_all()
        return courses
    
    def update_course_description(
        self,
        name: str,
        description: str,
    ) -> Course:
        course = self.get_course(name)
        if not course:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)
        
        course.description = description
        course = self.crud.update_course(course)
        return course


    def update_course(
        self,
        course_id: int,
        new_course: Course,
    ) -> Course:
        old_course: Course | None = self.crud.get_course_by_id(course_id)
        if not old_course:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)

        old_course.name = new_course.name
        old_course.description = new_course.description
        course = self.crud.update_course(old_course)

        return course


    def delete_course(
        self,
        id_or_name: str,
    ) -> bool:
        course = self.get_course(id_or_name)
        if not course:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)

        self.crud.delete_course(course)
        return