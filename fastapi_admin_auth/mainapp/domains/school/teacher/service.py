from typing import Any
from fastapi import Depends
# from .crud import (
#     get_teachers_all,
#     get_teachers_by_ids,
#     get_teachers_by_range,
#     get_teacher_by_id,
#     create_teacher,
#     update_teacher,
#     delete_teacher,
# )

# get_teachers_all
# get_teachers_by_ids
# get_teachers_by_range
# get_teacher_by_id
# create_teacher
# update_teacher
# delete_teacher
from mainapp.core.types.exceptions import HandledException, ResponseCode
from .models import Teacher
from .crud import TeacherCRUD


class TeacherService:
    def __init__(self):
        pass

    def __call__(
        self,
        crud: TeacherCRUD = Depends(TeacherCRUD()),
    ):
        self.crud = crud
        return self


    def add_new_teacher(
        self,
        teacher: dict[str, Any] | Teacher,
    ) -> Teacher:
        if isinstance(teacher, dict):
            teacher = Teacher(
                firstname=teacher["firstname"],
                lastname=teacher["lastname"],
                description=teacher.get("description"),
            )
        teacher = self.crud.create_teacher(teacher)
        return teacher


    def add_new_teachers(
        self,
        teacher_list: list[dict[str, Any] | Teacher],
    ) -> list[Teacher]:
        teachers = [self.add_new_teacher(teacher) for teacher in teacher_list]
        return teachers


    def get_teacher_by_name(
        self,
        firstname: str,
        lastname: str,
    ) -> Teacher | None:
        teacher = self.crud.get_teacher_by_name(firstname, lastname)
        return teacher


    def get_teacher_by_id_or_entity(
        self,
        id_or_entity: int | Teacher,
    ) -> Teacher | None:
        if isinstance(id_or_entity, int):
            teacher = self.crud.get_teacher_by_id(id_or_entity)
        elif isinstance(id_or_entity, Teacher):
            teacher = self.crud.get_teacher_by_id(id_or_entity.id)
        else:
            raise HandledException(ResponseCode.ENTITY_ID_INVALID)

        return teacher


    def get_teachers_all(
        self,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Teacher | None]:
        if page:
            teachers = self.crud.get_teachers_by_range(page=1)
        else:
            teachers = self.crud.get_teachers_all()
        return teachers
    
    def update_teacher_description(
        self,
        name: str,
        description: str,
    ) -> Teacher:
        teacher = self.get_teacher(name)
        if not teacher:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)
        
        teacher.description = description
        teacher = self.crud.update_teacher(teacher)
        return teacher


    def update_teacher(
        self,
        teacher_id: int,
        new_teacher: Teacher,
    ) -> Teacher:
        old_teacher: Teacher | None = self.crud.get_teacher_by_id(teacher_id)
        if not old_teacher:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)

        old_teacher.firstname = new_teacher.firstname
        old_teacher.lastname = new_teacher.lastname
        old_teacher.description = new_teacher.description
        teacher = self.crud.update_teacher(old_teacher)

        return teacher


    def delete_teacher(
        self,
        teacher_id: str,
    ) -> bool:
        teacher = self.get_teacher_by_id_or_entity(teacher_id)
        if not teacher:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)

        self.crud.delete_teacher(teacher)
        return
