from fastapi import APIRouter, Depends
# from mainapp.core.database import Session
from mainapp.core.exception_routers import HandledExceptionLoggingRoute
from mainapp.core.types.schema.response import CommonResponse
from .models import Teacher
from .service import TeacherService
from .schema import TeacherRequest


router = APIRouter(
    prefix="/teachers",
    tags=["teachers"],
    route_class=HandledExceptionLoggingRoute,
)


@router.get("")
async def get_teachers(
    firstname: str | None = None,
    lastname: str | None = None,
    service: TeacherService = Depends(TeacherService()),
):
    if firstname and lastname:
        teacher_or_teachers = [service.get_teacher_by_name(firstname, lastname)]
    else:
        teacher_or_teachers = service.get_teachers_all()
    return CommonResponse(data=teacher_or_teachers)


@router.post("")
async def add_teacher(
    body: TeacherRequest,
    service: TeacherService = Depends(TeacherService()),
    ):
    teacher: Teacher = service.add_new_teacher(
        teacher={
            "firstname": body.firstname,
            "lastname": body.lastname,
            "description": body.description,
        },
    )
    return CommonResponse(data=teacher)


@router.get("/{teacher_id}")
async def get_teacher_by_id(
    teacher_id: int,
    service: TeacherService = Depends(TeacherService()),
):
    teacher = service.get_teacher_by_id_or_entity(teacher_id)
    return CommonResponse(data=teacher)


@router.put("/{teacher_id}")
async def update_teacher(
    teacher_id: int,
    body: TeacherRequest,
    service: TeacherService = Depends(TeacherService()),
):
    
    teacher = service.update_teacher(teacher_id, body)
    return CommonResponse(data=teacher)


@router.delete("/{teacher_id}")
async def delete_teacher(
    teacher_id: int,
    service: TeacherService = Depends(TeacherService()),
):
    is_deleted = service.delete_teacher(teacher_id)
    return CommonResponse(
        data={
            "id": teacher_id,
            "is_deleted": is_deleted,
        }
    )
