from autologging import logged
from fastapi import FastAPI, APIRouter, Depends
import mainapp.core.config as core_config


@logged
def include_routers_by_config(
    app: FastAPI,
    routers: list[APIRouter],
    app_config: core_config.AppConfig = Depends(core_config.AppConfig),
) -> FastAPI:
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
