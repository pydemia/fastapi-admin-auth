
from mainapp.core.types.schema.request import BaseRequest
from mainapp.core.types.schema.response import CommonResponse

from pydantic import model_validator, ValidationError
# from ..textbook.schema import TextbookPublic

from .models import CourseBase, Certificate
from ..student.models import Student


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
    teacher_id: int
    students: list[int]


class UpdateCourseRequest(CreateCourseRequest):
    certificate_id: int | None = None
    certificate: CertificateRequest | None = None
    # certificte_id_or_certificate: int | CertificateRequest

    @model_validator(mode="before")
    def assign_certificate(cls, values):
        if values.get("certificate_id") is None and values.get("certificate") is None:
            raise ValidationError(
                "One of 'certificate_id' or 'certificate'"
            )
        return values


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

# class CoursePublic(Course): ...

class SingleCourseResponse(CommonResponse): ...

class MultiCourseResponse(CommonResponse): ...

class CoursePublic(CourseBase):
    id: int
    certificate: Certificate
    book_id: int | None
    certificate_id: int
    teacher_id: int
    students: list["Student"] = []

class SingleCourseWithStudentResponse(CommonResponse):
    data: CoursePublic | None = None

class MultiCourseWithStudentResponse(CommonResponse):
    data: list[CoursePublic] = []
