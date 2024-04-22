from mainapp.core.types.schema.request import BaseRequest


class StudentRequest(BaseRequest):
    firstname: str
    lastname: str
    description: str | None = ""
