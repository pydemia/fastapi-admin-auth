

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
        sa_relationship_kwargs={
            ## "lazy": "select",
            "lazy": "selectin",
            # "lazy": "joined",
            ## "lazy": "raise",
            # "lazy": "subquery",
            # "lazy": "write_only",
            # "lazy": "dynamic",
        },
    )

# seed = [
#     (
#         Student,
#         [
#             Student(id=0, firstname="Lucas", lastname="Young", description="student 0"),
#             Student(id=1, firstname="Christopher", lastname="Lee", description="student 1"),
#             Student(id=2, firstname="Sarah", lastname="Patel", description="student 2"),
#             Student(id=3, firstname="Liam", lastname="Davies", description="student 3"),
#             Student(id=4, firstname="Chloe", lastname="Bennett", description="student a"),
#             Student(id=5, firstname="Evelyn", lastname="Jones", description="student b"),
#         ]
#     ),
# ]
