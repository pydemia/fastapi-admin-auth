from mainapp.core.types.schema.request import BaseRequest
from mainapp.core.types.schema.response import CommonResponse

# from sqlmodel import SQLModel
# from ..textbook.schema import TextbookPublic
from .models import Course


class CourseRequest(BaseRequest):
    name: str
    description: str | None = ""
    book_id: int | None = None

# class CourseBase(SQLModel):
#     name: str
#     description: str | None = ""

# class CoursePublic(SQLModel):
#     id: int
#     book: TextbookPublic | None = None

# class SingleCourseResponse(CommonResponse):
#     data: CoursePublic | None = None

# class MultiCourseResponse(CommonResponse):
#     data: list[CoursePublic] = []


class SingleCourseResponse(CommonResponse):
    data: Course | None = None

class MultiCourseResponse(CommonResponse):
    data: list[Course] = []
