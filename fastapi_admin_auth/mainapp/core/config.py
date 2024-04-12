import os
from pathlib import Path
# from typing import Literal
from functools import partial

import pydantic
from autologging import logged
from pydantic.v1 import BaseSettings, Extra, Field, validator
from pydantic.v1.env_settings import SettingsSourceCallable

# # from pydantic.v1 import Field, validator, Extra
# # from pydantic.v1 import FilePath, DirectoryPath
# # from pydantic.v1.fields import FieldInfo
# from pydantic_settings import (
#     BaseSettings,
#     EnvSettingsSource,
#     PydanticBaseSettingsSource,
# )
from mainapp.core.types.enums import Locale

__all__ = [
    "AppConfig",
]


@logged
class AppSettings(BaseSettings):
    _root_key: str | None = None

    @pydantic.root_validator(pre=True)
    def _filter_by_root_key(cls, values):
        try:
            root_key = cls._root_key
        except AttributeError:
            root_key = None

        if "config" in values:
            values_to_use = values.pop("config")
        else:
            values_to_use = values
        if root_key is not None and str(root_key):
            values_to_use = values_to_use.get(str(root_key), {})

        values.update(values_to_use)
        return values

    class Config:
        underscore_attrs_are_private = False
        allow_mutation = False
        validate_all = True
        extra = Extra.ignore
        arbitrary_types_allowed = True
        case_sensitive = False

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            return env_settings, init_settings, file_secret_settings

    # @classmethod
    # def settings_customise_sources(
    #     cls,
    #     settings_cls: Type[BaseSettings],
    #     init_settings: PydanticBaseSettingsSource,
    #     env_settings: PydanticBaseSettingsSource,
    #     dotenv_settings: PydanticBaseSettingsSource,
    #     file_secret_settings: PydanticBaseSettingsSource,
    # ) -> Tuple[PydanticBaseSettingsSource, ...]:
    #     """
    #     Define the sources and their order for loading the settings values.

    #     Args:
    #         settings_cls: The Settings class.
    #         init_settings: The `InitSettingsSource` instance.
    #         env_settings: The `EnvSettingsSource` instance.
    #         dotenv_settings: The `DotEnvSettingsSource` instance.
    #         file_secret_settings: The `SecretsSettingsSource` instance.

    #     Returns:
    #         A tuple containing the sources and their order for loading the settings values.
    #     """
    #     return init_settings, env_settings, dotenv_settings, file_secret_settings


def to_dotted(string: str, prefix="database") -> str:
    return f"{prefix}.{string}"


class DBConfig(AppSettings):
    _root_key: str = "database"
    host: str = Field(os.getenv("DATABASE__HOST", os.getenv("SYSTEMDB__HOST", "quickdraw-admin")))
    port: int = Field(os.getenv("DATABASE__PORT", os.getenv("SYSTEMDB__PORT", "3306")))
    username: str = Field(os.getenv("DATABASE__USERNAME", os.getenv("SYSTEMDB__USERNAME", None)))
    password: str = Field(os.getenv("DATABASE__PASSWORD", os.getenv("SYSTEMDB__PASSWORD", None)))
    dbname: str = Field(os.getenv("DATABASE__DBNAME", os.getenv("SYSTEMDB__DBNAME", None)))

    class Config(AppSettings.Config):
        # env_prefix = "DATABASE__"
        extra = Extra.allow
        alias_generator = partial(to_dotted, prefix="database")

    @property
    def extra_fields(self) -> set[str]:
        return set(self.__dict__) - set(self.__fields__)


class JWTConfig(AppSettings):
    sso_url: str = Field(os.getenv("JWT__SSO_URL", "http://localhost:3001/dashboard/iam/checkUser/"))
    sso_url_authcode: str = Field(os.getenv("JWT__SSO_AUTHCODE_URL", "http://localhost:3001/dashboard/iam/authCode"))
    sso_url_callback: str = Field(os.getenv("JWT__SSO_TOKEN_URL", "http://localhost:3001/dashboard/iam/getToken/"))
    algorithm: str | None = "HS256"
    public_key: str | None
    default_userid: int = 0
    default_username: str = "quickdraw-admin"
    default_usergroup: int = 0
    use_test_token: bool = Field(
        description="If True, create a token for test and use it.",
        default=False,
    )


# class ConnectionCryptoKey(AppSettings):
#     key: str = Field(os.getenv("CRYPTO__CONNECTION__KEY", "quickdraw-admin"))


# class CryptoConfig(AppSettings):
#     _root_key: str = "crypto"
#     key: str = Field(os.getenv("CRYPTO_KEY", None))
#     connection: ConnectionCryptoKey


# class RedisConfig(AppSettings):
#     _root_key: str = "redis"
#     host: str = Field(os.getenv("REDIS__HOST", "redis"))
#     password: str = Field(os.getenv("REDIS__PASSWORD", None))
#     port: int = 6379
#     db: int = 0
#     charset: str = "utf-8"
#     decode_responses: bool = True


class AppConfig(AppSettings):
    _root_key: str = "app"
    name: str = "backend"
    version: str = "latest"
    root_path: str = "/api"
    log_level: str | None = Field(os.getenv("APP_PROFILE", os.getenv("LOG_LEVEL", "INFO")).upper())
    allowed_hosts: list[str] = ["*"]
    csrf_trusted_origins: list[str] = ["http://*", "https://*"]
    use_ns_nodeselector: bool = True
    locale: Locale = Locale.KO
    # jwt: JWTConfig = JWTConfig(algorithm="HS256", public_key=None)
    static_dir: Path = Field(Path(os.getenv("APP__STATIC_DIR", "static")))
    # mode: AppMode = AppMode(os.getenv("APP_MODE", "all")) # Literal["all", "gencode", "chatbot"]

    @validator("log_level", pre=True, always=True, allow_reuse=True)
    def set_log_level(cls, v):
        import logging

        log_level = v.upper() or "INFO"
        for logger_name in logging.root.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.setLevel(log_level)
