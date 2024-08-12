import datetime as dt
import logging

# from pydantic.v1 import BaseModel, Extra, root_validator
from pydantic import BaseModel, model_validator, ConfigDict
from pydantic.json import timedelta_isoformat

from mainapp.core.utils.misc import dt_to_timemilis

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

    model_config = ConfigDict(
        extra="allow",
        frozen=False,
        populate_by_name=True,
        json_encoders=json_encoders,
    )
    # class Config:
    #     extra = Extra.allow
    #     allow_mutation = True
    #     populate_by_name = True
    #     json_encoders = json_encoders


class ImmutableDTO(BaseDTO):
    model_config = ConfigDict(
        dict(
            BaseDTO.model_config,
            **ConfigDict(
                extra="allow",
                frozen=True,
            ),
        )
    )
    # class Config(BaseDTO.Config):
    #     extra = Extra.allow
    #     allow_mutation = False


class MutableDTO(BaseDTO):
    model_config = ConfigDict(
        BaseDTO.model_config,
        **dict(
            extra="allow",
            frozen=True,
        )
    )

    model_config = ConfigDict(
        dict(
            BaseDTO.model_config,
            **ConfigDict(
                extra="allow",
                frozen=False,
            ),
        )
    )
    # class Config(BaseDTO.Config):
    #     extra = Extra.allow
    #     allow_mutation = True

    @model_validator(mode="before")
    def __print_extra_fields__(cls, values):
        extra_fields = values.keys() - cls.model_fields.keys()
        if extra_fields:
            _class_name_ = cls.__name__
            extras = {e: values[e] for e in extra_fields}
            log = logging.getLogger(_class_name_)
            log.warning(f"extra fields in {_class_name_}: {extras}")
        return values


class ExtraForbiddenDTO(BaseDTO):
    model_config = ConfigDict(
        dict(
            BaseDTO.model_config,
            **ConfigDict(
                extra="forbid",
            ),
        )
    )
    # class Config(BaseDTO.Config):
    #     extra = Extra.forbid


class ExtraAllowedDTO(BaseDTO):
    model_config = ConfigDict(
        dict(
            BaseDTO.model_config,
            **ConfigDict(
                extra="allow",
                json_encoders={
                    dt.datetime: dt_to_timemilis,
                    dt.timedelta: timedelta_isoformat,
                }
            ),
        )
    )
    # class Config(BaseDTO.Config):
    #     extra = Extra.allow
    #     json_encoders = {
    #         dt.datetime: dt_to_timemilis,
    #         dt.timedelta: timedelta_isoformat,
    #     }

    @model_validator(mode="before")
    def __print_extra_fields__(cls, values):
        extra_fields = values.keys() - cls.model_fields.keys()
        if extra_fields:
            _class_name_ = cls.__name__
            extras = {e: values[e] for e in extra_fields}
            log = logging.getLogger(_class_name_)
            log.warning(f"extra fields in {_class_name_}: {extras}")
        return values


class ExtraIgnoredDTO(BaseDTO):
    model_config = ConfigDict(
        dict(
            BaseDTO.model_config,
            **ConfigDict(
                extra="ignore",
            ),
        )
    )
    # class Config(BaseDTO.Config):
    #     extra = Extra.ignore
