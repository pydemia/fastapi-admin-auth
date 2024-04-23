from fastapi import APIRouter, Depends
# from mainapp.core.database import Session
from mainapp.core.exception_routers import HandledExceptionLoggingRoute
from mainapp.core.types.schema.response import CommonResponse
from .models import Course
from .service import CourseService
from .schema import CourseRequest, SingleCourseResponse, MultiCourseResponse

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
    route_class=HandledExceptionLoggingRoute,
)


@router.get("", response_model=MultiCourseResponse)
async def get_courses(
    name: str | None = None,
    service: CourseService = Depends(CourseService()),
):
    if name:
        course_or_courses = [service.get_course(name)]
    else:
        course_or_courses = service.get_courses_all()
    # return CommonResponse(data=course_or_courses)
    return MultiCourseResponse(data=course_or_courses)


@router.post("")
async def add_course(
    body: CourseRequest,
    service: CourseService = Depends(CourseService()),
    ):
    course: Course = service.add_new_course(
        course=Course(
            name=body.name,
            description=body.description,
            book_id=body.book_id, 
        ),
    )
    return CommonResponse(data=course)


@router.get("/{course_id}", response_model=SingleCourseResponse)
async def get_course_by_id(
    course_id: int,
    service: CourseService = Depends(CourseService()),
):
    course = service.get_course(course_id)
    # return CommonResponse(data=course)
    return SingleCourseResponse(data=course)


@router.put("/{course_id}")
async def update_course(
    course_id: int,
    body: CourseRequest,
    service: CourseService = Depends(CourseService()),
):
    
    course = service.update_course(course_id, body)
    return CommonResponse(data=course)


@router.delete("/{course_id}")
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
