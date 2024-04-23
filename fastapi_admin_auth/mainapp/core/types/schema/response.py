import collections
import datetime as dt
from typing import Any

from pydantic.v1.json import timedelta_isoformat
from pydantic import BaseModel, Field, model_validator, ConfigDict

from mainapp.core.utils.misc import dt_to_timemilis
from ..exceptions import HandledException, ResponseCode, UnHandledException

__all__ = [
    "BaseResponse",
    "CommonResponse",
    "ErrorResponse",
    "Token",
]


class Result(dict):  # 5/6 heeseok : TypedDict --> Dict로 변경. TypedDict일때 기동 시 Type Exception 발생
    code: int
    message: str


class BaseResponse(BaseModel):
    timestamp: dt.datetime | None
    code: int | None
    message: str | None
    traceId: str | None
    data: Any | None = Field(
        None,
        title="the output",  # max_length=300
    )

    model_config = ConfigDict(
        json_encoders={
            dt.datetime: dt_to_timemilis,
            dt.timedelta: timedelta_isoformat,
        }
    )
    # class Config:
    #     underscore_attrs_are_private = True
    #     # max_anystr_length = 1_000_000
    #     error_msg_templates = {
    #         "value_error.any_str.max_length": "max_length:{limit_value}",
    #     }
    #     json_encoders = {
    #         dt.datetime: dt_to_timemilis,
    #         dt.timedelta: timedelta_isoformat,
    #     }
    #     # arbitrary_types_allowed = True


class CommonResponse(BaseResponse):
    @model_validator(mode="before")
    def _init(cls, values):
        values["timestamp"] = dt.datetime.utcnow()
        rc = ResponseCode.SUCCESS
        values["code"] = rc.code
        values["message"] = rc.message
        values["traceId"] = None
        return values


class ErrorResponse(CommonResponse):
    @model_validator(mode="before")
    def _init(cls, values):
        values["timestamp"] = dt.datetime.utcnow()
        if "e" in values:
            e: Exception | HandledException = values["e"]
        c: int | None = values.get("code", None)
        if isinstance(e, (HandledException, UnHandledException)):
            if c is None:
                code = e.code
                message = e.systemMessage
            else:
                code = c.code
                message = c.message
        else:
            if c is None:
                c = ResponseCode.UNDEFINED_ERROR
            e = HandledException(c, e=e)
            code = e.code
            message = e.message
            values["e"] = e
        values["code"] = code
        values["message"] = message
        values["traceId"] = e.traceId
        return values


class Token(BaseModel):
    access_token: str
    token_type: str
    statusCode: int
    content: dict | None


def _recursive_update_dt_to_timemilis(old, new=None):
    if old is None or not isinstance(old, collections.Mapping):
        return old
    else:
        if isinstance(old, BaseModel):
            old = old.to_dict()
        for _key, _val in old.items():
            if isinstance(_val, collections.Mapping):
                old[_key] = _recursive_update_dt_to_timemilis(
                    old.get(_key, type(_val)()),
                    _val,
                )
            elif isinstance(_val, dt.datetime):
                old[_key] = dt_to_timemilis(_val)
            return old
