from mainapp.core.types.schema.request import BaseRequest


class TextbookRequest(BaseRequest):
    name: str
    description: str | None = ""
