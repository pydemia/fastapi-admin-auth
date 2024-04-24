from mainapp.core.types.schema.request import BaseRequest
from mainapp.core.types.schema.response import CommonResponse

# from sqlmodel import SQLModel
# from ..textbook.schema import TextbookPublic
from .models import Course


class CourseRequestBase(BaseRequest):
    name: str
    description: str | None = ""


class CourseRequest(CourseRequestBase):
    book_id: int | None = None
    certificate_id: int


class CertificateRequest(BaseRequest):
    name: str
    description: str | None = ""


class CreateCourseRequest(BaseRequest):
    name: str
    description: str | None = ""
    book_id: int | None = None
    certificate: CertificateRequest

class UpdateCourseRequest(BaseRequest):
    name: str
    description: str | None = ""
    book_id: int | None = None
    certificte_id_or_certificate: int | CertificateRequest


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
