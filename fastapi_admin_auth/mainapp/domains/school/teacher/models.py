

__all__ = [
    "Teacher",
]

from sqlmodel import Field, SQLModel


class Teacher(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    firstname: str
    lastname: str
    description: str = Field("")
