import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from autologging import logged
from mainapp.core.iam import view as iam_view
from mainapp.domain.health import view as health_view
from mainapp.core import dependencies
from mainapp.core.dependencies import (
    Container,
    get_container,
    include_routers_by_config,
)
from mainapp.core.iam.idp import idp

@logged
def create_app() -> FastAPI:

    container: Container = get_container(
        wire_modules=list(set([
            # idp,
            iam_view,
            dependencies,
        ])),
    )

    app = FastAPI(
        title="FastAPI-Admin-Auth",
        description="""This is a sample FastAPI application with authentication and authorization features.
        """,
        root_path=container.app_config().root_path,
        dependencies=[],
    )
    idp.add_swagger_config(app)
    # from mainapp.core.dependencies import add_swagger_config
    # app = add_swagger_config(app)

    # routers = [
    #     iam_view.router,
    #     health_view.router,
    # ]
    # for router in routers:
    #     app.include_router(router)
    app = include_routers_by_config(
        app,
        routers=[
            iam_view.router,
            health_view.router,
        ],
    )
    
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    log_level = os.getenv("APP_PROFILE", os.getenv("LOG_LEVEL", "INFO")).upper()
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)

    return app

app = create_app()
