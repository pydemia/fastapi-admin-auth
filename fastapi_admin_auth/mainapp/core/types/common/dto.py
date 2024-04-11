import datetime as dt
import logging

from pydantic import BaseModel, Extra, root_validator
from pydantic.json import timedelta_isoformat

from ...utils.misc import dt_to_timemilis

__all__ = [
    "CODE_FIELD_MAX_LENGTH",
    "BaseDTO",
    "ImmutableDTO",
    "MutableDTO",
    "ExtraForbiddenDTO",
    "ExtraAllowedDTO",
    "ExtraIgnoredDTO",
]


json_encoders = {
    dt.datetime: dt_to_timemilis,
    dt.timedelta: timedelta_isoformat,
    str: str,
    int: str,
    float: str,
}

CODE_FIELD_MAX_LENGTH = 100_000


class BaseDTO(BaseModel):
    class Config:
        extra = Extra.allow
        allow_mutation = True
        populate_by_name = True
        json_encoders = json_encoders


class ImmutableDTO(BaseDTO):
    class Config(BaseDTO.Config):
        extra = Extra.allow
        allow_mutation = False


class MutableDTO(BaseDTO):
    class Config(BaseDTO.Config):
        extra = Extra.allow
        allow_mutation = True

    @root_validator(pre=True)
    def __print_extra_fields__(cls, values):
        extra_fields = values.keys() - cls.__fields__.keys()
        if extra_fields:
            _class_name_ = cls.__name__
            extras = {e: values[e] for e in extra_fields}
            log = logging.getLogger(_class_name_)
            log.warning(f"extra fields in {_class_name_}: {extras}")
        return values


class ExtraForbiddenDTO(BaseDTO):
    class Config(BaseDTO.Config):
        extra = Extra.forbid


class ExtraAllowedDTO(BaseDTO):
    class Config(BaseDTO.Config):
        extra = Extra.allow
        json_encoders = {
            dt.datetime: dt_to_timemilis,
            dt.timedelta: timedelta_isoformat,
        }

    @root_validator(pre=True)
    def __print_extra_fields__(cls, values):
        extra_fields = values.keys() - cls.__fields__.keys()
        if extra_fields:
            _class_name_ = cls.__name__
            extras = {e: values[e] for e in extra_fields}
            log = logging.getLogger(_class_name_)
            log.warning(f"extra fields in {_class_name_}: {extras}")
        return values


class ExtraIgnoredDTO(BaseDTO):
    class Config(BaseDTO.Config):
        extra = Extra.ignore
