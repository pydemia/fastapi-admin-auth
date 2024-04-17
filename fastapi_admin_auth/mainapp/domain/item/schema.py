from mainapp.core.types.schema.request import BaseRequest


class ItemRequest(BaseRequest):
    name: str
    description: str | None = ""
