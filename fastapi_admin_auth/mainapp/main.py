import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from autologging import logged
from mainapp.core.iam.view import add_swagger_config
from mainapp.core import iam
from mainapp.core.containers import Container, get_container


@logged
def create_app() -> FastAPI:

    container: Container = get_container(
        wire_modules=list(set([
            iam.view,
        ])),
    )

    app = FastAPI(
        title="FastAPI-Admin-Auth",
        description="""This is a sample FastAPI application with authentication and authorization features.
        """,
        root_path=container.app_config().root_path,
        dependencies=[],
    )
    app = add_swagger_config(app)

    # app.include_router(router)
    routers = [
        iam.view.router,
    ]
    for router in routers:
        app.include_router(router)
    
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
