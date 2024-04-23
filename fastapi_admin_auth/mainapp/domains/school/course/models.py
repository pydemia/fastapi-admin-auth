

__all__ = [
    "Course",
]

# from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from ..textbook.models import Textbook


class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str = Field("")
    book_id: int | None = Field(default=None, foreign_key="textbook.id")
    book: Textbook | None = Relationship(
    # book: Textbook | None = Relationship(
        # back_populates="textbook.id",
        # sa_relationship_kwargs=dict(
        #     lazy="selectin",
        # )
    )
