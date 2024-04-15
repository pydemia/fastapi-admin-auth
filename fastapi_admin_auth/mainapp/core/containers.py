# from types import ModuleType
# from collections import namedtuple
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
from mainapp.core import config as core_config
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

    db_config = providers.Factory(
        core_config.DBConfig,
        config=config,
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

    # debug_service = providers.Factory(
    #     services.DebugService,
    #     app_config=app_config,
    # )
    # chat_service = providers.Factory(
    #     services.ChatService,
    #     app_config=app_config,
    #     llm_endpoint_config=llm_endpoint_config,
    #     model_engine_config=model_engine_config,
    #     # redis_config=redis_config,
    #     # redis=redis,
    #     llm_endpoint=llm_endpoint,
    # )

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
    yaml_file = os.getenv("APP_CONFIG", "config.yaml")
    container.config.from_yaml(yaml_file, envs_required=False)
    # aa = container.config()
    container.init_resources()

    container.wire(modules=[__name__] + wire_modules)

    from mainapp.core.config import DBConfig

    # ss = AppSettings()
    dd = DBConfig()
    return container


@logged
@inject
def include_routers(
    app: fastapi.FastAPI,
    routers: list[fastapi.APIRouter],
    app_config: core_config.AppConfig = Provide[Container.app_config],
) -> fastapi.FastAPI:
    # from corusapi.api import routers
    # from mainapp.core import iam
    # # from corusapi.utils.common import is_installed_app

    # included_routers: list[fastapi.APIRouter]
    # included_routers = [
    #     iam.view.router,
    # ]
    # if is_installed_app("corusadmin.project"):
    #     included_routers += [
    #         routers.project.router,
    #         routers.project.router_ver,
    #     ]

    # if is_installed_app("corusadmin.code"):
    #     code_routers = [
    #         routers.code.router,
    #         routers.code.router_ver,
    #         routers.tabby.router,
    #     ]
    # else:
    #     code_routers = []

    # if is_installed_app("corusadmin.chat"):
    #     chat_routers = [
    #         routers.chat.router,
    #         routers.chat.router_ver,
    #         routers.tabby.router,
    #     ]
    # else:
    #     chat_routers = []

    # user_routers = [routers.user.router, routers.user.router_ver] if is_installed_app("corusadmin.iam") else []

    # prompt_routers = [routers.prompt.router, routers.prompt.router_ver] if is_installed_app("corusadmin.prompt") else []

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
    # included_routers += code_routers
    # included_routers += chat_routers
    # included_routers += user_routers
    # included_routers += prompt_routers

    for router in routers:
        app.include_router(router)

    return app
