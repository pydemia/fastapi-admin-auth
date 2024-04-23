from mainapp.core.types.schema.request import BaseRequest
from mainapp.core.types.schema.response import CommonResponse

from sqlmodel import SQLModel


class TextbookRequest(BaseRequest):
    name: str
    description: str | None = ""


class TextbookBase(SQLModel):
    name: str
    description: str | None = ""

class TextbookPublic(SQLModel):
    id: int

class SingleTextbookResponse(CommonResponse):
    data: TextbookPublic | None = None

class MultiTextbookResponse(CommonResponse):
    data: list[TextbookPublic] = []
