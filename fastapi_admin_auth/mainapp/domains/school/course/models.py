

__all__ = [
    "Course",
]

# from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from starlette.requests import Request

from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ..textbook.models import Textbook
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


class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str = Field("")

    book_id: int | None = Field(default=None, foreign_key="textbook.id")
    book: Optional["Textbook"] = Relationship()

    # certificate_id: int | None = Field(foreign_key="certificate.id")
    certificate_id: int | None = Field(foreign_key="certificate.id")
    certificate: "Certificate" = Relationship(
        back_populates="course",
        sa_relationship_kwargs={
            "cascade": "all",
            # "cascade": "save-update, delete", # Instruct the ORM how to track changes to local objects
            # "lazy": "selectin",
        },
    )

    # async def __admin_repr__(self, request: Request):
    #     return self.name