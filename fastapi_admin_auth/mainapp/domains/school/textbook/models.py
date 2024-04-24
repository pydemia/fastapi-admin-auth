

__all__ = [
    "Textbook",
]

from sqlmodel import Field, SQLModel
from starlette.requests import Request


class Textbook(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str = Field("")
    body: str = Field(default="This is a sample textbook body.")

    async def __admin_repr__(self, request: Request):
        return self.name
