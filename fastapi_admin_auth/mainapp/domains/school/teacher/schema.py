from mainapp.core.types.schema.request import BaseRequest


class TeacherRequest(BaseRequest):
    firstname: str
    lastname: str
    description: str | None = ""
