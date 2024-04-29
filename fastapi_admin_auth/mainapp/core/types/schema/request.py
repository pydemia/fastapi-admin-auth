from autologging import logged
from fastapi import Header
from httpx import URL
# from pydantic.v1 import BaseModel, Extra, validator
from pydantic import BaseModel, ConfigDict, field_validator

from ..common.fields import CPUField, GPUField, MEMField

__all__ = [
    "HttpRequestHeaders",
    "http_request_headers",
    "ResourceSpec",
    "PageRequest",
    "PredictorSpec",
    "BaseRequest",
]


class BaseRequest(BaseModel):

    model_config: ConfigDict = ConfigDict(
        extra="allow",
        frozen=True,
    )
    # class Config:
    #     extra = Extra.allow
    #     allow_mutation = False


class PredictorSpec(BaseModel):
    min_replica: int
    max_replica: int
    type: str
    runtime_version: str
    storage_uri: str
    image: str
    modelclass_name: str | None


@logged
class ResourceSpec(BaseModel):
    res_mem_req: float = MEMField
    res_cpu_req: float = CPUField
    res_gpu_req: int | None = GPUField
    res_mem_limit: float = MEMField
    res_cpu_limit: float = CPUField
    res_gpu_limit: int | None = GPUField
    # replica_min: int                # 최소 Replica
    # replica_max: int                # 최대 Replica

    @field_validator("res_cpu_limit", mode="before")
    def validate_cpu_minmax(cls, v, values, **kwargs):
        if v < values["res_cpu_req"]:
            cls._ResourceSpec__log.warn(
                f"'cpu_limit' [{v}] is smaller than 'cpu_request' [{values['res_cpu_req']}]."
                + f"replacing it with 'cpu_request' [{values['res_cpu_req']}]..."
            )
            return values["res_cpu_req"]
        else:
            return float(v)

    @field_validator("res_mem_limit", mode="before")
    def validate_mem_minmax(cls, v, values, **kwargs):
        cls._ResourceSpec__log.info(values)
        if v < values["res_mem_req"]:
            cls._ResourceSpec__log.warn(
                f"'mem_limit' [{v}] is smaller than 'mem_request' [{values['res_mem_req']}]."
                + f"replacing it with 'mem_request' [{values['res_mem_req']}]..."
            )
            return values["res_mem_req"]
        else:
            return v

    @field_validator("res_gpu_limit", mode="plain")
    def validate_gpu_minmax(cls, v, values, **kwargs):
        if v < values["res_gpu_req"]:
            cls._ResourceSpec__log.warn(
                f"'gpu_limit' [{v}] is smaller than 'gpu_request' [{values['res_gpu_req']}]."
                + f"replacing it with 'gpu_request' [{values['res_gpu_req']}]..."
            )
            return values["res_gpu_req"]
        else:
            return v


class PageRequest(BaseModel):
    """API: /models"""

    page: int = 0
    size: int = 50
    sort: str | None = None
    direction: bool = True
    find: str | None = None


class HttpRequestHeaders(BaseModel):
    usergroup: str | None = None
    referer: str | None = None
    origin: str | None = None


async def http_request_headers(
    usergroup: str | None = Header(None),
    referer: str | None = Header(None),
    origin: str | None = Header(None),
) -> HttpRequestHeaders:
    headers = HttpRequestHeaders(usergroup=usergroup, referer=referer, origin=origin)
    if headers.origin is None:
        if headers.referer is not None:
            url = URL(headers.referer)
            headers.origin = f"{url.scheme}://{url.netloc.decode()}"
    return headers
