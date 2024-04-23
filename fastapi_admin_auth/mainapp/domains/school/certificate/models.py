

__all__ = [
    "Certificate",
]

from sqlmodel import Field, SQLModel


class Certificate(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    firstname: str
    lastname: str
    description: str = Field("")
