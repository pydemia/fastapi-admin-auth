

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

seed = [
    (
        Textbook,
        [
            Textbook(id=0, name="textbook 0", description="textbook_0"),
            Textbook(id=1, name="textbook 1", description="textbook_1"),
            Textbook(id=2, name="textbook 2", description="textbook_2"),
            Textbook(id=3, name="textbook 3", description="textbook_3"),
        ],
    )
]
