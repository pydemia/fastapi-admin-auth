

__all__ = [
    "Teacher",
]


from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from ..course.models import Course

class Teacher(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    firstname: str
    lastname: str
    description: str = Field("")

    courses: list["Course"] = Relationship(
            back_populates="teacher"
    )