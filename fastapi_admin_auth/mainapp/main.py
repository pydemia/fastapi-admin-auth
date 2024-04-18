import os
import logging.config
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from autologging import logged
from mainapp.core import config
from mainapp.core.dependencies import (
    include_routers_by_config,
)
from mainapp.core.iam.idp import idp
from mainapp.core.database import db


from mainapp.core.iam import view as iam_view
from mainapp.domain.health import view as health_view
from mainapp.domain.item import view as item_view


from mainapp.domain.health import models as health_models
from mainapp.domain.item import models as item_models

from mainapp.core.admin import admin

@logged
def create_app() -> FastAPI:
    app_config = config.AppConfig()
    db.create_database(
        [
            health_models,
            item_models,
        ]
    )

    ROOT_PATH = config.app_config.root_path
    app = FastAPI(
        title="FastAPI-Admin-Auth",
        description="""This is a sample FastAPI application with authentication and authorization features.
        """,
        root_path=ROOT_PATH,
        dependencies=[],
        version=app_config.version,
    )
    idp.add_swagger_config(app)

    app = include_routers_by_config(
        app,
        routers=[
            iam_view.router,
            health_view.router,
            item_view.router,
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

    app.mount(
        "/static",
        StaticFiles(directory=Path(__file__).parent.joinpath("static")),
        name="static",
    )

    @app.get("/", include_in_schema=False)
    async def redirect_root():
        return RedirectResponse(url=f"{ROOT_PATH}/docs")

    @app.get("/iam", include_in_schema=False)
    async def redirect_iam():
        return RedirectResponse(url=config.keyclock_config.server_url)


    # @app.get("/dashboard/static", include_in_schema=False)
    # async def redirect_admin_static():
    #     return RedirectResponse(url="/static")

    admin.add_view(item_models.ItemModelView)
    admin.mount_to(app)

    logging.config.fileConfig("logging.conf", disable_existing_loggers=False,)
    log_level = os.getenv("APP_PROFILE", os.getenv("LOG_LEVEL", "INFO")).upper()
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)

    return app

app = create_app()
