

__all__ = [
    "Course",
]

# from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from starlette.requests import Request

from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ..textbook.models import Textbook
    from ..teacher.models import Teacher
    from ..student.models import Student
# from mainapp.domains.school.textbook import models as textbook_models
# from mainapp.domains.school.certificate import models as certificate_models


class Certificate(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str = Field("")

    # course_id: int | None = Field(default=None, foreign_key="course.id")
    course: "Course" = Relationship(
        back_populates="certificate",
        # sa_relationship_kwargs={
        #     "lazy": "selectin",
        # }
    )

    async def __admin_repr__(self, request: Request):
        return self.name



class CourseStudentLink(SQLModel, table=True):
    # See another-self: https://github.com/tiangolo/sqlmodel/issues/89#issuecomment-917698160
    course_id: int | None = Field(
        default=None,
        foreign_key="course.id",
        primary_key=True,
    )
    student_id: int | None = Field(
        default=None,
        foreign_key="student.id",
        primary_key=True,
    )


class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str = Field("")

    book_id: int | None = Field(default=None, foreign_key="textbook.id")
    book: Optional["Textbook"] = Relationship()

    # certificate_id: int | None = Field(foreign_key="certificate.id")
    certificate_id: int = Field(foreign_key="certificate.id")
    certificate: "Certificate" = Relationship(
        back_populates="course",
        sa_relationship_kwargs={
            "cascade": "all",
            # "cascade": "save-update, delete", # Instruct the ORM how to track changes to local objects
            "lazy": "selectin",
        },
    )

    teacher_id: int = Field(foreign_key="teacher.id")
    teacher: "Teacher" = Relationship(
            back_populates="courses"
    )

    students: list["Student"] = Relationship(
        back_populates="courses",
        link_model=CourseStudentLink,
        sa_relationship_kwargs={
            # "cascade": "save-update, delete", # Instruct the ORM how to track changes to local objects
            # "lazy": "selectin",  # "subquery"
            "lazy": "subquery",
        },
    )

    # async def __admin_repr__(self, request: Request):
    #     return self.name

# cert_4 = Certificate(id=4, name="cert 4", description="cert_4")
# teacher_3 = Teacher(id=3, firstname="Charlotte", lastname="Wilson", description="teacher 4")

# seed = [
#     (
#         "Textbook",
#         [
#             # Textbook(id=4, name="textbook a", description="textbook_a"),
#             # Textbook(id=5, name="textbook b", description="textbook_b"),
#             dict(id=6, name="textbook A", description="textbook_A"),
#             dict(id=7, name="textbook B", description="textbook_B"),
#         ]
#     ),
#     (
#         "Student",
#         [
#             dict(id=1, firstname="Christopher", lastname="Lee", description="student 1"),
#             dict(id=2, firstname="Sarah", lastname="Patel", description="student 2"),
#             dict(id=3, firstname="Liam", lastname="Davies", description="student 3"),
#             dict(id=4, firstname="Lucas", lastname="Young", description="student 4"),
#             dict(id=5, firstname="Chloe", lastname="Bennett", description="student a"),
#             dict(id=6, firstname="Evelyn", lastname="Jones", description="student b"),
#         ]
#     ),
#     (
#         "Teacher",
#         [
#             # Teacher(id=1, firstname="Sophia", lastname="Garcia", description="teacher 1", courses=[1, 2]),
#             # Teacher(id=2, firstname="Ethan", lastname="Miller", description="teacher 2", courses=[]),
#             # Teacher(id=3, firstname="Charlotte", lastname="Wilson", description="teacher 3", courses=[2, 3]),
#             # Teacher(id=4, firstname="Daniel", lastname="Walker", description="teacher 4", courses=[1, 2]),
#             # Teacher(id=5, firstname="Scarlett", lastname="Lewis", description="teacher a", courses=[3]),
#             # Teacher(id=6, firstname="Audrey", lastname="Taylor", description="teacher b", courses=[1, 2, 3]),
            
#             dict(id=1, firstname="Sophia", lastname="Garcia", description="teacher 1"),
#             dict(id=2, firstname="Ethan", lastname="Miller", description="teacher 2"),
#             dict(id=3, firstname="Charlotte", lastname="Wilson", description="teacher 3"),
#             dict(id=4, firstname="Daniel", lastname="Walker", description="teacher 4"),
#             # dict(id=4, firstname="Scarlett", lastname="Lewis", description="teacher a"),
#             # dict(id=5, firstname="Audrey", lastname="Taylor", description="teacher b"),
#         ],
#     ),
#     (
#         "Certificate",
#         [
#             dict(id=1, name="cert 1", description="cert_1"),
#             dict(id=2, name="cert 2", description="cert_2"),
#             dict(id=3, name="cert 3", description="cert_3"),
#             dict(id=4, name="cert 4", description="cert_4"),
#             dict(id=5, name="cert 5", description="cert_5"),
#         ]
#     ),
#     (
#         "Course",
#         [
#             dict(id=1, name="course 1", description="course_1", certificate_id=1, teacher_id=1),
#             dict(id=2, name="course 2", description="course_2", certificate_id=2, teacher_id=1, students=[1]),
#             dict(id=3, name="course 3", description="course_3", certificate_id=3, teacher_id=4, students=[2, 3]),
#             dict(id=4, name="course 4", description="course_4", certificate_id=4, teacher_id=3, students=[1, 3, 4]),
#             dict(id=5, name="course 5", description="course_5", certificate_id=5, teacher_id=2, students=[6, 1]),
#             # Course(id=4, name="course 3", description="course_4", certificate=cert_4, teacher_id=2),
#             # dict(id=1, name="course 1", description="course_1", certificate_id=1, teacher_id=1, students=[0, 5]),
#             # dict(id=2, name="course 2", description="course_2", certificate_id=2, teacher_id=1, students=[1, 3, 5]),
#             # dict(id=3, name="course 3", description="course_3", certificate_id=3, teacher_id=0, students=[3, 4, 5]),
#             # Course(id=0, name="course 0", description="course_0", courses=[0, 1]),
#             # Course(id=1, name="course 1", description="course_1", courses=[0, 2]),
#             # Course(id=2, name="course 2", description="course_2", courses=[]),
#             # Course(id=3, name="course 3", description="course_3", courses=[2, 3]),
#         ],
#     )
# ]
