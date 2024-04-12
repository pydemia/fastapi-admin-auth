# from types import ModuleType
# from collections import namedtuple
import importlib
import os
from functools import lru_cache

import fastapi
from autologging import logged
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject


# from corusapi import database

# # from corusapi import history
# # from corusapi.history import base as historyclient
# from corusapi.api import services
# from corusapi.core import config as core_config
# from corusapi.llm import endpoints

# from ..database.crud import (
#     CodeRequestHistoryRepository,
#     LlmEndpointConfigRepository,
#     UserResponseAnalyticsRepository
# )


__all__ = [
    "Container",
    "get_container",
]


@logged
class Container(containers.DeclarativeContainer):
    """ """

    config: providers.Configuration
    db: providers.ThreadSafeSingleton
    # db_redis: providers.ThreadSafeSingleton
    history: providers.ThreadSafeSingleton
    jwt_auth_manager: providers.ThreadSafeSingleton
    app_config: providers.Configuration
    crypto_config: providers.Configuration
    websocket_config: providers.Configuration
    llm_endpoint_config: providers.Configuration
    outputs_git_config: providers.Configuration
    faiss_config: providers.Configuration
    smtp_config: providers.Configuration
    orchestration_config: providers.Configuration

    user_repository: providers.Factory

    config = providers.Configuration()

    # db_config = providers.Factory(
    #     core_config.DBConfig,
    #     config=config,
    # )

    faiss_config = providers.Factory(
        core_config.FaissConfig,
        config=config,
    )

    redis_config = providers.Factory(
        core_config.RedisConfig,
        config=config,
    )

    redis = providers.ThreadSafeSingleton(
        database.RedisDataBase,
        redis_config=redis_config,
    )

    # db = providers.ThreadSafeSingleton(
    #     database.Database,
    #     db_config=config
    # )
    # opensearch_client = providers.ThreadSafeSingleton(
    #     historyclient.OpenSearchClient,
    #     opensearch_config=opensearch_config
    # )

    app_config = providers.Factory(
        core_config.AppConfig,
        config=config,
    )
    opensearch_config = providers.Factory(
        core_config.OpensearchConfig,
        config=config,
    )
    crypto_config = providers.Factory(
        core_config.CryptoConfig,
        config=config,
    )
    websocket_config = providers.Factory(
        core_config.WebsocketConfig,
        config=config,
    )
    llm_endpoint_config = providers.Factory(
        core_config.LLMEndpointConfig,
        config=config,
    )
    model_engine_config = providers.Factory(
        core_config.ModelEngineConfig,
        config=config,
    )
    outputs_git_config = providers.Factory(
        core_config.OutputsGitConfig,
        config=config,
    )
    # SMTP Config, add 2023.9.1 kim dong-hun
    smtp_config = providers.Factory(
        core_config.SMTPConfig,
        config=config,
    )
    # add 2024.2.10 kim dong-hun
    orchestration_config = providers.Factory(
        core_config.OrchestrationConfig,
        config=config,
    )

    llm_endpoint = providers.Factory(
        endpoints.LLMEndpoint,
        llm_endpoint_config=llm_endpoint_config,
        model_engine_config=model_engine_config,
    )

    debug_service = providers.Factory(
        services.DebugService,
        app_config=app_config,
    )
    chat_service = providers.Factory(
        services.ChatService,
        app_config=app_config,
        llm_endpoint_config=llm_endpoint_config,
        model_engine_config=model_engine_config,
        # redis_config=redis_config,
        # redis=redis,
        llm_endpoint=llm_endpoint,
    )
    # llm_endpoint_config_repository = providers.Factory(
    #     LlmEndpointConfigRepository,
    #     session_factory=db.provided.session
    # )
    # code_req_history_repository = providers.Factory(
    #     CodeRequestHistoryRepository,
    #     session_factory=db.provided.session
    # )
    # user_response_analytics_repository = providers.Factory(
    #     UserResponseAnalyticsRepository,
    #     session_factory=db.provided.session
    # )
    code_req_service = providers.Factory(
        services.CodeService,
        # code_req_history_repo=code_req_history_repository,
        llm_endpoint_config=llm_endpoint_config,
        outputs_git_config=outputs_git_config,
        faiss_config=faiss_config,
    )
    user_response_analytics_service = providers.Factory(
        services.UserResponseAnalyticsService,
        # user_response_analytics_repo=user_response_analytics_repository
    )
    # 계정 생성/패스워드 초기화 서비스, add 2023.9.1 kim dong-hun
    user_service = providers.Factory(
        services.UserService,
        smtp_config=smtp_config,
    )
    orchestration_service = providers.Factory(
        services.OrchestrationService,
    )

    projectrepo_service = providers.Factory(
        services.ProjectRepoService,
    )


def hash_list(l: list) -> int:
    __hash = 0
    for i, e in enumerate(l):
        __hash = hash((__hash, i, hash_item(e)))
    return __hash


def hash_dict(d: dict) -> int:
    __hash = 0
    for k, v in d.items():
        __hash = hash((__hash, k, hash_item(v)))
    return __hash


def hash_item(e) -> int:
    if hasattr(e, "__hash__") and callable(e.__hash__):
        try:
            return hash(e)
        except TypeError:
            pass
    if isinstance(e, list | set | tuple):
        return hash_list(list(e))
    if isinstance(e, (dict)):
        return hash_dict(e)

    raise TypeError(f"unhashable type: {e.__class__}")


def _lru_cache(*opts, **kwopts):
    def decorator(func):
        def wrapper(*args, **kwargs):
            __hash = hash_item([id(func)] + list(args) + list(kwargs.items()))

            @lru_cache(*opts, **kwopts)
            def cached_func(args_hash):
                return func(*args, **kwargs)

            return cached_func(__hash)

        return wrapper

    return decorator


@_lru_cache(maxsize=None)
def get_container(wire_modules=[]) -> Container:
    container = Container()
    container.config.from_yaml(os.getenv("APP_CONFIG", "config.yaml"), envs_required=False)
    container.init_resources()

    container.wire(modules=[__name__] + wire_modules)

    return container


@logged
@inject
# def include_routers_by_mode(
def include_routers(
    app: fastapi.FastAPI,
    app_config: core_config.AppConfig = Provide[Container.app_config],
) -> fastapi.FastAPI:
    from corusapi.api import routers
    from corusapi.utils.common import is_installed_app

    included_routers: list[fastapi.APIRouter]
    included_routers = [
        routers.auth.router,
        routers.auth.router_ver,
        routers.debug.router,
        routers.debug.router_ver,
        routers.health.router,
        routers.health.router_ver,
        routers.llm.router,
        routers.prompt.router,
        routers.prompt.router_ver,
        routers.orchestration.router,
        routers.flow.router_ver,
    ]
    if is_installed_app("corusadmin.project"):
        included_routers += [
            routers.project.router,
            routers.project.router_ver,
        ]

    if is_installed_app("corusadmin.code"):
        code_routers = [
            routers.code.router,
            routers.code.router_ver,
            routers.tabby.router,
        ]
    else:
        code_routers = []

    if is_installed_app("corusadmin.chat"):
        chat_routers = [
            routers.chat.router,
            routers.chat.router_ver,
            routers.tabby.router,
        ]
    else:
        chat_routers = []

    user_routers = [routers.user.router, routers.user.router_ver] if is_installed_app("corusadmin.iam") else []

    prompt_routers = [routers.prompt.router, routers.prompt.router_ver] if is_installed_app("corusadmin.prompt") else []

    #     if app_config.mode == AppMode.ALL:
    #         included_routers += code_routers
    #         included_routers += chat_routers
    #         included_routers += user_routers
    #         included_routers += prompt_routers
    #     elif app_config.mode == AppMode.GENCODE:
    #         included_routers += code_routers
    #         included_routers += user_routers
    #         included_routers += prompt_routers
    #     elif app_config.mode == AppMode.CHATBOT:
    #         included_routers += chat_routers
    #         included_routers += user_routers
    #         included_routers += prompt_routers

    # Add ALL routers
    included_routers += code_routers
    included_routers += chat_routers
    included_routers += user_routers
    included_routers += prompt_routers

    for router in included_routers:
        app.include_router(router)

    container: Container = get_container()

    if container.orchestration_config().vertical_apps is not None:
        for ap in container.orchestration_config().vertical_apps:
            try:
                if ap["type"] == "fastapi":
                    files = os.listdir(os.getcwd() + "/" + ap["name"].replace(".", "/"))
                    modules = [m.removesuffix(".py") for m in files if m not in ("__init__.py", "__pycache__")]
                    for m in modules:
                        v_module = importlib.import_module(f"{ap['name']}.{m}")
                        app.include_router(v_module.router)
            except (ModuleNotFoundError, ImportError, AttributeError):  # noqa: PERF203
                include_routers._log.exception(f"Failed to include router for {ap['name']}")

    for app_name in settings.INSTALLED_APPS:
        if app_name.startswith("apps."):
            try:
                router_mod = importlib.import_module(f"{app_name}.routers")
                router = router_mod.router
                app.include_router(router)

            except (ModuleNotFoundError, ImportError, AttributeError):
                include_routers._log.exception(f"Failed to include router for {app_name}")

    return app
