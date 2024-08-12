
from typing import Optional
from pydantic import Field
from mainapp.core.types.common.base import ExtraIgnoredDTO


__all__ = [
    "S3Credential",
    "BlobCredential",
]

class S3Credential(ExtraIgnoredDTO):
    """_summary_
    """
    accesskey: Optional[str] = Field(alias="fs.s3a.access.key", description="접근 키", default="")
    secretkey: Optional[str] = Field(alias="fs.s3a.secret.key", description="암호화 키", default="")
    endpoint: Optional[str] = Field(alias="fs.s3a.endpoint", description="endpoint", default="")
    bucketName: Optional[str] = Field(description="버킷 이름", default="")


class BlobCredential(ExtraIgnoredDTO):
    """_summary_
    """
    accessKey: Optional[str] = Field(description="접근 키", default="")
    account: Optional[str] = Field(description="account", default="")
    container: Optional[str] = Field(description="컨테이너", default="")
    id: Optional[int] = Field(description="id", default=-1)
    name: Optional[str] = Field(description="접속 이름", default="")

