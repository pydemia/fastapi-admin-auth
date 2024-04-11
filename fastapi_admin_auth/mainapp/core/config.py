import os
from pathlib import Path
from typing import Literal

import pydantic
from autologging import logged
from pydantic import BaseSettings, Extra, Field, validator
from pydantic.env_settings import SettingsSourceCallable

# from pydantic.v1 import Field, validator, Extra
# from pydantic.v1 import FilePath, DirectoryPath
# from pydantic.v1.fields import FieldInfo
# from pydantic_settings import (
#     BaseSettings,
#     EnvSettingsSource,
#     PydanticBaseSettingsSource,
# )
from corusapi.types.enums import LLMType, Locale

__all__ = [
    "AppConfig",
    "WebsocketConfig",
    "LLMEndpointConfig",
    "OutputsGitConfig",
    "OpensearchConfig",
    "SMTPConfig",
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


# class DBConfig(AppSettings):
#     _root_key: str = "database"
#     host: str = Field(os.getenv("DATABASE__HOST", os.getenv("SYSTEMDB__HOST", "quickdraw-admin")))
#     port: int = Field(os.getenv("DATABASE__PORT", os.getenv("SYSTEMDB__PORT", "3306")))
#     username: str = Field(os.getenv("DATABASE__USERNAME", os.getenv("SYSTEMDB__USERNAME", None)))
#     password: str = Field(os.getenv("DATABASE__PASSWORD", os.getenv("SYSTEMDB__PASSWORD", None)))
#     dbname: str = Field(os.getenv("DATABASE__DBNAME", os.getenv("SYSTEMDB__DBNAME", None)))

#     class Config(AppSettings.Config):
#         # env_prefix = "DATABASE__"
#         extra = Extra.allow
#         alias_generator = partial(to_dotted, prefix="database")

#     @property
#     def extra_fields(self) -> Set[str]:
#         return set(self.__dict__) - set(self.__fields__)


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


class ConnectionCryptoKey(AppSettings):
    key: str = Field(os.getenv("CRYPTO__CONNECTION__KEY", "quickdraw-admin"))


class CryptoConfig(AppSettings):
    _root_key: str = "crypto"
    key: str = Field(os.getenv("CRYPTO_KEY", None))
    connection: ConnectionCryptoKey


class RedisConfig(AppSettings):
    _root_key: str = "redis"
    host: str = Field(os.getenv("REDIS__HOST", "redis"))
    password: str = Field(os.getenv("REDIS__PASSWORD", None))
    port: int = 6379
    db: int = 0
    charset: str = "utf-8"
    decode_responses: bool = True


class AppConfig(AppSettings):
    _root_key: str = "app"
    name: str = "corusapi"
    version: str = "latest"
    root_path: str = "/api"
    log_level: str | None = Field(os.getenv("APP_PROFILE", os.getenv("LOG_LEVEL", "INFO")).upper())
    sentry_dsn: str = ""
    sentry_environment: str = "localhost"
    allowed_hosts: list[str] = ["*"]
    csrf_trusted_origins: list[str] = ["http://*", "https://*"]
    use_ns_nodeselector: bool = True
    locale: Locale = Locale.KO
    jwt: JWTConfig = JWTConfig(algorithm="HS256", public_key=None)
    static_dir: Path = Field(Path(os.getenv("APP__STATIC_DIR", "static")))
    # mode: AppMode = AppMode(os.getenv("APP_MODE", "all")) # Literal["all", "gencode", "chatbot"]

    @validator("log_level", pre=True, always=True, allow_reuse=True)
    def set_log_level(cls, v):
        import logging

        log_level = v.upper() or "INFO"
        for logger_name in logging.root.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.setLevel(log_level)


class OpensearchConfig(AppSettings):
    _root_key: str = "opensearch"
    host: str = os.getenv("OPENSEARCH__HOST", "https://opensearch.corus-ai.net")
    port: int = os.getenv("OPENSEARCH__PORT", 9200)
    username: str = os.getenv("OPENSEARCH__USERNAME", "admin")
    password: str = os.getenv("OPENSEARCH__PASSWORD", "admin")
    use_ssl: bool = os.getenv("OPENSEARCH__SSL", True)
    verify_certs: bool = os.getenv("OPENSEARCH__CERTS", True)
    cacert: str | None = os.getenv("OPENSEARCH__CACERT", None)
    # cert: Optional[str] = os.getenv("OPENSEARCH__CERT", None)
    # certkey: Optional[str] = os.getenv("OPENSEARCH__CERTKEY", None)


class HistoryConfig(AppSettings):
    _root_key: str = "history"
    storage_type: Literal["systemdb", "opensearch"] = Field(os.getenv("HISTORY__STORAGE_TYPE", "systemdb"))


class WebsocketConfig(AppSettings):
    _root_key: str = "websocket"
    host: str = "http://localhost"
    port: int = 8080
    username: str = os.getenv(" WEBSOCKET_USERNAME", "admin")
    password: str = os.getenv(" WEBSOCKET_PASSWORD", "admin")


class LLMConfig(AppSettings):
    endpoint_name: str
    llm_type: LLMType

    class Config(AppSettings.Config):
        extra = Extra.allow


class AzureOpenAIConfig(LLMConfig):
    model_name: str = Field(description="The name of the model to use.", default="gpt-35-turbo")
    resource_name: str = os.getenv("LLM_ENDPOINT__AZURE_OPENAI__OPENAI_RESOURCE_NAME", "openai-quickdraw")
    deployment_name: str = os.getenv("LLM_ENDPOINT__AZURE_OPENAI__OPENAI_DEPLOYMENT_NAME", "quickdraw-ai")
    api_key: str = os.getenv("LLM_ENDPOINT__AZURE_OPENAI__API_KEY")
    api_version: str = os.getenv("LLM_ENDPOINT__AZURE_OPENAI__API_VERSION", "2023-05-15")
    # operation_name: str = os.getenv("LLM_ENDPOINT__AZURE_OPENAI__OPERATION_NAME", "chat/completions")


class OpenAIConfig(LLMConfig):
    model_name: str = Field(description="The name of the model to use.", default="gpt-35-turbo")
    resource_name: str = os.getenv("OPENAI_RESOURCE_NAME", "openai-quickdraw")
    deployment_name: str = os.getenv("OPENAI_DEPLOYMENT_NAME", "quickdraw-ai")
    api_key: str = os.getenv("API_KEY")
    api_version: str = os.getenv("API_VERSION", "2023-05-15")
    # operation_name: str = os.getenv("OPERATION_NAME", "chat/completions")


class GooglePalmConfig(LLMConfig):
    model_name: str = Field(description="The name of the model to use.", default="gpt-35-turbo")
    resource_name: str = os.getenv("OPENAI_RESOURCE_NAME", "openai-quickdrawai")
    deployment_name: str = os.getenv("OPENAI_DEPLOYMENT_NAME", "quickdraw-ai")
    api_key: str = os.getenv("API_KEY")
    api_version: str = os.getenv("API_VERSION", "2023-05-15")
    # operation_name: str = os.getenv("OPERATION_NAME", "chat/completions")


class ModelEngineConfig(AppSettings):
    _root_key: str = "model_engine"
    system_prompt: str = os.getenv(
        "MODEL_ENGINE_CONFIG__SYSTEM_PROMPT",
        "The following is a conversation with an AI assistant. The corus is helpful, creative, clever, and very friendly.",
    )
    context_length: int = Field(3, multiple_of=1, ge=0, le=100)
    context_time: int = Field(300, multiple_of=1, ge=10, le=3600, description="seconds")


class LLMEndpointConfig(AppSettings):
    _root_key: str = "llm_endpoint"
    endpoints: list[AzureOpenAIConfig | OpenAIConfig | GooglePalmConfig]
    # azure_openai: Optional[List[AzureOpenAIConfig]]
    # openai: Optional[List[OpenAIConfig]]
    # google_palm: Optional[GooglePalmConfig]
    # model_engine: Optional[ModelEngineConfig]
    system_prompt: str = os.getenv("CORUS_CHAT_SYSTEM_PROMPT")
    prompt_engine_url: str = os.getenv("PROMPT_ENGINE_URL", "http://localhost:8001/prompt/call")


class OutputsGitConfig(AppSettings):
    _root_key: str = "outputs_git"
    remote_url: str = os.getenv("REMOTE_URL", "https://github.com/skcc-cloud-ai-tech/ai-coding-backend.git")
    origin_dir: str = os.getenv("ORIGIN_DIR", "/workspace/outputs_git/outputs_git")


class FaissConfig(AppSettings):
    _root_key: str = "faiss"
    endpoint: str | None = os.getenv("FAISS_URL", "http://app.quickdrawai.net/api/faiss/backend/faiss/search")


class OpensearchConfig(AppSettings):
    _root_key: str = "opensearch"
    host: str = os.getenv("OPENSEARCH__HOST", "https://opensearch.corus-ai.net")
    port: int = os.getenv("OPENSEARCH__PORT", 9200)
    username: str = os.getenv("OPENSEARCH__USERNAME", "admin")
    password: str = os.getenv("OPENSEARCH__PASSWORD", "admin")
    use_ssl: bool = os.getenv("OPENSEARCH__SSL", True)
    verify_certs: bool = os.getenv("OPENSEARCH__CERTS", True)
    cacert: str = os.getenv("OPENSEARCH_CACERT", None)


# SMTP Config, add 2023.9.1 kim dong-hun
class SMTPConfig(AppSettings):
    _root_key: str = "smtp"
    server_type: str = os.getenv("SMTP_SERVER_TYPE", "azure")
    connection_string: str = os.getenv(
        "SMTP_CONNECTION_STRING",
        "endpoint=https://corus-email-comm.unitedstates.communication.azure.com/;accesskey=+Lv9Ps+JDNwwTexyTm6s6P5EzhVEcS0dqu8MT1eCmShW/A3iVD4Dj9jsTID79NTKAzkjxZJaBfpL3Y5fgCdbdA==",
    )
    from_mail: str = os.getenv("SMTP_FROM_MAIL", "DoNotReply@4af00481-d7ac-4522-9236-654394d6cfc0.azurecomm.net")
    from_name: str = os.getenv("SMTP_FROM_NAME", "G.AI Engineering2 Team")
    corus_url: str = os.getenv("SMTP_CORUS_URL", "http://app.corus-ai.net")
    allows_email: str = os.getenv("SMTP_ALLOWS_EMAIL", "sk.com, skcc.com")
    manual_url: str = os.getenv(
        "SMTP_MANUAL_URL",
        "https://www.notion.so/SKCC-AICoding-280dcccf64f847e89aa526ef8ffba255?pvs=4",
    )


class OrchestrationConfig(AppSettings):
    _root_key: str = "orchestration"
    vertical_apps: list[dict[str, str]] = os.getenv("ORCHESTRATION_VERTICAL_APPS", None)
    installed_apps: list[dict[str, str]] = os.getenv("ORCHESTRATION_INSTALLED_APPS", None)
