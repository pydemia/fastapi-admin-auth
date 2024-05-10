from fastapi import APIRouter, Depends
# from mainapp.core.database import Session
from mainapp.core.exception_routers import HandledExceptionLoggingRoute
from mainapp.core.types.schema.response import CommonResponse
from .models import Course, Certificate
from .service import CourseService
from .schema import (
    CreateCourseRequest,
    UpdateCourseRequest,
    SingleCourseResponse,
    MultiCourseWithStudentResponse,
    SingleCourseWithStudentResponse,
    CertificateRequest,
)
from ..student.service import StudentService

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
    route_class=HandledExceptionLoggingRoute,
)


@router.get(
    "",
    response_model=MultiCourseWithStudentResponse,
)
async def get_courses(
    name: str | None = None,
    service: CourseService = Depends(CourseService()),
):
    if name:
        course_or_courses = [service.get_course(name)]
    else:
        course_or_courses = service.get_courses_all()
    return MultiCourseWithStudentResponse(data=course_or_courses)


@router.get(
    "/{course_id}",
    response_model=SingleCourseWithStudentResponse,
)
async def get_course_by_id(
    course_id: int,
    service: CourseService = Depends(CourseService()),
):
    course = service.get_course(course_id)
    # return CommonResponse(data=course)
    return SingleCourseWithStudentResponse(data=course)


@router.post(
    "",
    response_model=SingleCourseResponse,
)
async def add_course(
    body: CreateCourseRequest,
    service: CourseService = Depends(CourseService()),
    student_service: StudentService = Depends(StudentService())
    ):
    body_dict = body.model_dump(exclude_unset=True)
    if body.certificate:
        body_dict["certificate"] = Certificate.model_validate(body.certificate.model_dump(exclude_unset=True))
    if body.students:
        body_dict["students"] = [
            student_service.get_student_by_id_or_entity(s)
            for s in body.students
        ]
    course = Course(**body_dict)
    course: Course = service.add_new_course(
        course=course
    )
    return SingleCourseResponse(data=course)


@router.put(
    "/{course_id}",
    response_model=SingleCourseWithStudentResponse,
)
async def update_course(
    course_id: int,
    body: UpdateCourseRequest,
    service: CourseService = Depends(CourseService()),
):
    new_course = body
    course = service.update_course(course_id, new_course)
    return SingleCourseWithStudentResponse(data=course)


@router.delete(
    "/{course_id}",
    response_model=CommonResponse,
)
async def delete_course(
    course_id: int,
    service: CourseService = Depends(CourseService()),
):
    is_deleted = service.delete_course(course_id)
    return CommonResponse(
        data={
            "id": course_id,
            "is_deleted": is_deleted,
        }
    )



@router.get(
    "",
    response_model=CommonResponse,
)
async def get_certificates(
    name: str | None = None,
    service: CourseService = Depends(CourseService()),
):
    if name:
        cert_or_certs = [service.get_course(name)]
    else:
        cert_or_certs = service.get_courses_all()
    return CommonResponse(data=cert_or_certs)


@router.get(
    "/{certificate_id}",
    response_model=CommonResponse,
)
async def get_certificate_by_id(
    certificate_id: int,
    service: CourseService = Depends(CourseService()),
):
    course = service.get_course(certificate_id)
    # return CommonResponse(data=course)
    return CommonResponse(data=course)


@router.put(
    "/{certificate_id}",
    response_model=CommonResponse,
)
async def update_certificate(
    certificate_id: int,
    body: CertificateRequest,
    service: CourseService = Depends(CourseService()),
):
    new_cert = body
    course = service.update_certificate(certificate_id, new_cert)
    return CommonResponse(data=course)


# @router.delete("/{certificate_id}")
# async def delete_certificates(
#     certificate_id: int,
#     service: CourseService = Depends(CourseService()),
# ):
#     is_deleted = service.delete_course(certificate_id)
#     return CommonResponse(
#         data={
#             "id": certificate_id,
#             "is_deleted": is_deleted,
#         }
#     )
