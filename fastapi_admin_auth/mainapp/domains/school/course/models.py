

__all__ = [
    "Course",
]

from sqlmodel import Field, SQLModel


class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str = Field("")
    
