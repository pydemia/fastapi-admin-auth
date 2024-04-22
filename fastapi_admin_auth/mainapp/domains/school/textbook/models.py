

__all__ = [
    "Textbook",
]

from sqlmodel import Field, SQLModel


class Textbook(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str = Field("")
    body: str = Field(default="This is a sample textbook body.")
