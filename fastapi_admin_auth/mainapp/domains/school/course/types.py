from typing import Optional
from pydantic import Field
from mainapp.core.types.enums import BaseEnum
from mainapp.core.types.common import ExtraIgnoredDTO


__all__ = [
    
]


class S3Credential(ExtraIgnoredDTO):
    """_summary_
    """
    accesskey: Optional[str] = Field(alias="fs.s3a.access.key", description="접근 키", default="")
    secretkey: Optional[str] = Field(alias="fs.s3a.secret.key", description="암호화 키", default="")
    endpoint: Optional[str] = Field(alias="fs.s3a.endpoint", description="endpoint", default="")
    bucketName: Optional[str] = Field(description="버킷 이름", default="")


class FrameworkType(BaseEnum):
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    SKLEARN = "sklearn"
    ONNX = "onnx"
    TRITON = "triton"
    XGBOOST = "xgboost"
    CUSTOM = "custom"
