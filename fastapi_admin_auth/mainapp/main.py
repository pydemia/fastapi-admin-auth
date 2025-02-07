import os
import logging.config
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from autologging import logged
from mainapp.core import config
from mainapp.core.dependencies import mount_domains
from mainapp.core.iam.oauth import idp
from mainapp.core.database import db
from mainapp.core.global_exception_handlers import set_global_exception_handlers
from mainapp.core.middlewares import BackgroundTaskExceptionMiddleware
# from mainapp.domains import (
#     example,
#     school,
# )

def prepare_db():
    logging.info("DB: creating tables...")
    # db.create_database(
    #     sum(
    #         [
    #             example.domain_models,
    #             school.domain_models,
    #         ],
    #         [],
    #     )
    # )
    logging.info("DB: apply migrations...")
    
    # db.apply_migration()
    # db.insert_seed()
    
    logging.info("DB: setup finished.")


@logged
def create_app() -> FastAPI:
    app_config = config.AppConfig()
    # db.create_database(
    #     sum(
    #         [
    #             example.domain_models,
    #             school.domain_models,
    #         ],
    #         [],
    #     )
    # )
    # prepare_db()
    db.prepare()

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

    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        BackgroundTaskExceptionMiddleware,
        handlers=app.exception_handlers,
    )
    app = set_global_exception_handlers(app)
    

    app.mount(
        "/static",
        StaticFiles(directory=Path(__file__).parent.joinpath("static")),
        name="static",
    )

    # @app.get("/", include_in_schema=False)
    # async def redirect_root(request: Request):
    #     return RedirectResponse(url=f"{ROOT_PATH}/docs")

    @app.get("/", include_in_schema=False)
    async def redirect_root(request: Request):
        return RedirectResponse(url=f'{request.scope.get("root_path")}/dashboard')
        # return RedirectResponse(url=f'/dashboard')

    @app.get("/iam", include_in_schema=False)
    async def redirect_iam():
        return RedirectResponse(url=config.keyclock_config.server_url)


    logging.config.fileConfig("logging.conf", disable_existing_loggers=False,)
    log_level = os.getenv("APP_PROFILE", os.getenv("LOG_LEVEL", "INFO")).upper()
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)


    # @app.get("/dashboard/static", include_in_schema=False)
    # async def redirect_admin_static():
    #     return RedirectResponse(url="/static")


    # from mainapp.core.admin import admin
    # from mainapp.domains.item.admin import ItemView
    # admin.add_view(ItemView)

    # from mainapp.domains.school.student.admin import (
    #     StudentView,
    #     # AuthorizedItemView,
    #     # ActionedItemView,
    # )
    # admin.add_view(StudentView)
    # # admin.add_view(AuthorizedItemView)
    # # admin.add_view(ActionedItemView)

    # from mainapp.domains.school.textbook.admin import (
    #     TextbookView,
    #     # ActionedDocumentView,
    # )
    # admin.add_view(TextbookView)
    # # admin.add_view(ActionedDocumentView)


    # from mainapp.domains.school.course.admin import CourseView
    # admin.add_view(CourseView)
    
    # from mainapp.domains.school.teacher.admin import TeacherView
    # admin.add_view(TeacherView)


    # app = include_routers_by_config(
    #     app,
    #     routers=[
    #         health_router,
    #         iam_router,
    #         example.domain_router,
    #         school.domain_router,
    #     ]
    # )
    # from mainapp.core.admin import admin, add_admin_views
    # admin = add_admin_views(admin, example.domain_adminviews)
    # admin = add_admin_views(admin, school.domain_adminviews)
    # admin.mount_to(app)

    app = mount_domains(
        app,
        # modules=[
        #     example,
        #     school,
        # ]
        # modules=[
        #     'example',
        #     'school',
        # ]
        modules=app_config.domains
    )


    return app

app = create_app()
