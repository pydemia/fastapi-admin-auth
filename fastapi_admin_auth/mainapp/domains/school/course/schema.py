from mainapp.core.types.schema.request import BaseRequest


class CourseRequest(BaseRequest):
    name: str
    description: str | None = ""
