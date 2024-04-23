from mainapp.core.types.schema.request import BaseRequest


class CertificateRequest(BaseRequest):
    firstname: str
    lastname: str
    description: str | None = ""
