from typing import Dict
import functools
import inspect
import os
from functools import lru_cache

import fastapi
from autologging import logged
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Header, Request
from fastapi_keycloak import FastAPIKeycloak
from typing_extensions import Annotated

from mainapp.core import config as core_config
from mainapp.core import database
# from mainapp.core.idp import get_idp, add_swagger_config


# from mainapp.core.types.enums.code import ClientType


__all__ = [
    "Container",
    "get_container",
    "get_client_ip",
    "include_routers_by_config",
]

# async def get_token_header(x_token: str = Header(...)):
#     if x_token != "fake-super-secret-token":
#         raise HTTPException(status_code=400, detail="X-Token header invalid")


# async def get_query_token(token: str):
#     if token != "jessica":
#         raise HTTPException(
#             status_code=400, detail="No Jessica token provided")


async def get_session(request: Request):
    # here I get sqlalchemy's scoped_session, which should be the same instance per thread
    request.state.session = request.app.state.database.get_session()
    try:
        yield request.state.session
    finally:
        request.state.session.close()


async def managed_transaction(func):

    @functools.wraps(func)
    async def wrap_func(*args, session: Session = Depends(get_session), **kwargs):
        try:
            if inspect.iscoroutinefunction(func):
                result = await func(*args, session=session, **kwargs)
            else:
                result = func(*args, session=session, **kwargs)
            session.commit()
        except HTTPException as e:
            session.rollback()
            raise e
        # don't close session here, or you won't be able to response
        return result

    return wrap_func



async def get_client_ip(
        x_real_ip: Annotated[str, Header()] = None,
        x_forwarded_for: Annotated[str, Header()] = None,
        ) -> Dict[str, str]:

    return {
        "x_real_ip": x_real_ip,
        "x_forwarded_for": x_forwarded_for,
    }

# @inject
# def get_idp(config: Provide["keycloak_config"]):
#     idp = FastAPIKeycloak(
#         server_url=config.server_url,
#         client_id=config.client_id,
#         client_secret=config.client_secret,
#         admin_client_id=config.admin_client_id,
#         admin_client_secret=config.admin_client_secret,
#         realm=config.realm,
#         callback_uri=config.callback_uri,
#     )
#     return idp

# @inject
# def add_swagger_config(
#     app: FastAPI,
#     idp: FastAPIKeycloak = Provide["idp"],
# ) -> FastAPI:
#     idp.add_swagger_config(app)
#     return app


# @inject
# class IDProvider:
#     def __init__(
#         self,
#         keycloak_config = Provide["keycloak_config"],
#     ) -> None:
#         self.config = keycloak_config
#         self.idp = FastAPIKeycloak(
#             server_url=self.config.server_url,
#             client_id=self.config.client_id,
#             client_secret=self.config.client_secret,
#             admin_client_id=self.config.admin_client_id,
#             admin_client_secret=self.config.admin_client_secret,
#             realm=self.config.realm,
#             callback_uri=self.config.callback_uri,
#         )
#     def add_app(self, app: FastAPI) -> FastAPI:
#         self.idp.add_swagger_config(app)
#         return app



@logged
class Container(containers.DeclarativeContainer):
    """ """

    config: providers.Configuration
    db: providers.ThreadLocalSingleton
    # db_redis: providers.ThreadSafeSingleton
    history: providers.ThreadSafeSingleton
    jwt_auth_manager: providers.ThreadSafeSingleton
    app_config: providers.Configuration
    keycloak_config: providers.Configuration
    idp: providers.ThreadSafeSingleton

    user_repository: providers.Factory

    config = providers.Configuration()

    db_config = providers.Factory(
        core_config.DBConfig,
        config=config,
    )

    db = providers.ThreadSafeSingleton(
        database.Database,
        db_config=config
    )

    keycloak_config = providers.Factory(
        core_config.KeycloakConfig,
        config=config,
    )
    # idp = providers.Factory(
    #     FastAPIKeycloak,
    #     server_url=keycloak_config.server_url,
    #     client_id=keycloak_config.client_id,
    #     client_secret=keycloak_config.client_secret,
    #     admin_client_id=keycloak_config.admin_client_id,
    #     admin_client_secret=keycloak_config.admin_client_secret,
    #     realm=keycloak_config.realm,
    #     callback_uri=keycloak_config.callback_uri,
    # )
    idp = providers.Factory(
        FastAPIKeycloak,
        server_url=core_config.KeycloakConfig().server_url,
        client_id=core_config.KeycloakConfig().client_id,
        client_secret=core_config.KeycloakConfig().client_secret,
        admin_client_id=core_config.KeycloakConfig().admin_client_id,
        admin_client_secret=core_config.KeycloakConfig().admin_client_secret,
        realm=core_config.KeycloakConfig().realm,
        callback_uri=core_config.KeycloakConfig().callback_uri,
    )

    # idp = providers.ThreadSafeSingleton(
    #     get_idp,
    #     config=keycloak_config,
    # )
    # idp = providers.Callable(
    #     get_idp,
    #     config=keycloak_config,
    # )
    # idp = providers.ThreadSafeSingleton(
    #     FastAPIKeycloak,
    #     server_url=keycloak_config.server_url,
    #     client_id=keycloak_config.client_id,
    #     client_secret=keycloak_config.client_secret,
    #     admin_client_id=keycloak_config.admin_client_id,
    #     admin_client_secret=keycloak_config.admin_client_secret,
    #     realm=keycloak_config.realm,
    #     callback_uri=keycloak_config.callback_uri,
    # )
    # idp_get_current_user = providers.Callable(idp_get_current_user)
    # idp = providers.ThreadSafeSingleton(
    #     IDProvider,
    #     keycloak_config=keycloak_config,
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

    # from mainapp.core.config import DBConfig

    # # ss = AppSettings()
    # dd = DBConfig()
    return container


@logged
@inject
def include_routers_by_config(
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
