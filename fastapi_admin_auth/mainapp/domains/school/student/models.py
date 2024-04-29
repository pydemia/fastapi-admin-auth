

__all__ = [
    "Student",
]

from sqlmodel import Field, SQLModel, Relationship
from typing import TYPE_CHECKING

from ..course.models import CourseStudentLink
if TYPE_CHECKING:
    from ..course.models import Course


class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    firstname: str
    lastname: str
    description: str = Field("")

    courses: list["Course"] = Relationship(
        back_populates="students",
        link_model=CourseStudentLink,
    )
