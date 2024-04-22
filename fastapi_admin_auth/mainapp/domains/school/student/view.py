from fastapi import APIRouter, Depends
# from mainapp.core.database import Session
from mainapp.core.exception_routers import HandledExceptionLoggingRoute
from mainapp.core.types.schema.response import CommonResponse
from .models import Student
from .service import StudentService
from .schema import StudentRequest


router = APIRouter(
    prefix="/students",
    tags=["school/students"],
    route_class=HandledExceptionLoggingRoute,
)


@router.get("")
async def get_students(
    firstname: str | None = None,
    lastname: str | None = None,
    service: StudentService = Depends(StudentService()),
):
    if firstname and lastname:
        student_or_students = service.get_student_by_name(firstname, lastname)
    else:
        student_or_students = service.get_students_all()
    return CommonResponse(data=student_or_students)


@router.post("")
async def add_student(
    body: StudentRequest,
    service: StudentService = Depends(StudentService()),
    ):
    student: Student = service.add_new_student(
        student={
            "firstname": body.firstname,
            "lastname": body.lastname,
            "description": body.description,
        },
    )
    return CommonResponse(data=student)


@router.get("/{student_id}")
async def get_student_by_id(
    student_id: int,
    service: StudentService = Depends(StudentService()),
):
    student = service.get_student_by_id_or_entity(student_id)
    return CommonResponse(data=student)


@router.put("/{student_id}")
async def update_student(
    student_id: int,
    body: StudentRequest,
    service: StudentService = Depends(StudentService()),
):
    
    student = service.update_student(student_id, body)
    return CommonResponse(data=student)


@router.delete("/{student_id}")
async def delete_student(
    student_id: int,
    service: StudentService = Depends(StudentService()),
):
    is_deleted = service.delete_student(student_id)
    return CommonResponse(
        data={
            "id": student_id,
            "is_deleted": is_deleted,
        }
    )
