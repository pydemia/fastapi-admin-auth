from typing import Literal, Any
import os
from pathlib import Path
# from typing import Literal

from autologging import logged
# from pydantic.v1 import BaseSettings, Extra, Field, validator
# from pydantic.v1.env_settings import SettingsSourceCallable

# # from pydantic.v1 import Field, validator, Extra
# # from pydantic.v1 import FilePath, DirectoryPath
# # from pydantic.v1.fields import FieldInfo
# from pydantic_settings import (
#     BaseSettings,
#     EnvSettingsSource,
#     PydanticBaseSettingsSource,
# )


from pydantic import Field, field_validator, model_validator
from typing import Type
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)
from pydantic_settings.sources import import_yaml
import yaml
import re

from mainapp.core.types.enums import Locale

__all__ = [
    "AppConfig",
]

class EnvYamlConfigSettingsSource(YamlConfigSettingsSource):

    def _read_file(self, file_path: Path) -> dict[str, Any]:
        import_yaml()
        with open(file_path, encoding=self.yaml_file_encoding) as yaml_file:
            yaml_str = yaml_file.read()
            env_pattern = re.compile(".*?\${(\w+)}.*?")
            enved = env_pattern.findall(yaml_str)
            if enved:
                for env in enved:
                    yaml_str = yaml_str.replace(
                        f"${{{env}}}", os.environ.get(env, f"${{{env}}}")
                    )

            # return yaml.safe_load(yaml_file)
            return yaml.safe_load(yaml_str)


@logged
class AppSettings(BaseSettings):
    _root_key: str | None = None

    @model_validator(mode="before")
    def _filter_by_root_key(cls, values):
        try:
            root_key = cls._root_key.get_default()
        except AttributeError:
            root_key = None

        if "config" in values:
            values_to_use = values.pop("config")
        else:
            values_to_use = values
        if root_key is not None and str(root_key):
            values_to_use = values_to_use.get(str(root_key), {})

        # values.update(values_to_use)
        values = values_to_use
        return values

    model_config = SettingsConfigDict(
        env_prefix="",
        env_nested_delimiter="__",
        yaml_file=os.getenv("APP_CONFIG", "config.yaml"),
        frozen=False,
        validate_default=True,
        arbitrary_types_allowed=True,
        case_sensitive=True,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return init_settings, env_settings, file_secret_settings, EnvYamlConfigSettingsSource(settings_cls)


def to_dotted(string: str, prefix="database") -> str:
    return f"{prefix}.{string}"


class DBConfig(AppSettings):
    _root_key: str = "database"
    driver: Literal["mysql", "postgresql"] = Field("mysql")
    host: str = Field(os.getenv("DATABASE__HOST", "localhost"))
    port: int = Field(os.getenv("DATABASE__PORT", "3306"))
    username: str = Field(os.getenv("DATABASE__USERNAME", "admin"))
    password: str = Field(os.getenv("DATABASE__PASSWORD", "admin"))
    dbname: str = Field(os.getenv("DATABASE__DBNAME", "backend"))

    AppSettings.model_config.update(
        dict(
            extra="allow",
            # alias_generator=partial(to_dotted, prefix="database"),
        )
    )

    @property
    def extra_fields(self) -> set[str]:
        return set(self.__dict__) - set(self.model_fields)


class KeycloakConfig(AppSettings):
    _root_key: str = "keycloak"
    server_url: str = Field("http://localhost:8080")
    client_id: str = Field("fastapi-admin-auth-app")
    client_secret: str = Field("iRJRjyNKZ3zqbwW3NXHJLhTgbMT20SPM")
    admin_client_id: str = Field("admin-cli")
    admin_client_secret: str = Field("WJmdud32rsQ4TzbPuGiU1V6pPWhOH8pq")
    realm: str = "fastapi-admin-auth"
    callback_uri: str = "http://localhost:8000/callback"

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

    @field_validator("log_level", mode="before")
    def set_log_level(cls, v):
        import logging

        log_level = v.upper() or "INFO"
        for logger_name in logging.root.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.setLevel(log_level)
