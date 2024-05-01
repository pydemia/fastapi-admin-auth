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
from mainapp.core.iam.oauth import idp
from mainapp.core.database import db


from mainapp.core.iam.routes import router as iam_router
# from mainapp.domains.health import view as health_view
# from mainapp.domains.item import view as item_view
# from mainapp.domains.school.textbook import view as textbook_view
# from mainapp.domains.school.student import view as student_view
# from mainapp.domains.school.teacher import view as teacher_view
# from mainapp.domains.school.course import view as course_view
from mainapp.domains import (
    example,
    school,
)


# from mainapp.domains.health import models as health_models
# from mainapp.domains.item import models as item_models
# from mainapp.domains.school.textbook import models as textbook_models
# from mainapp.domains.school.student import models as student_models
# from mainapp.domains.school.teacher import models as teacher_models
# from mainapp.domains.school.course import models as course_models

# from mainapp.core.domains import import_domain_components, add_admin_views
# domain_router, admin_views, domain_models = import_domain_components(school)

# @asynccontextmanager
# async def prepare_db(app_: FastAPI):
#     logging.info("DB: creating tables...")
#     # db.create_database(
#     #     sum(
#     #         [
#     #             example.domain_models,
#     #             school.domain_models,
#     #         ],
#     #         [],
#     #     )
#     # )
#     logging.info("DB: apply migrations...")
#     db.apply_migration()
#     yield
#     logging.info("DB: setup finished.")

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
    db.apply_migration()
    logging.info("DB: setup finished.")


@logged
def create_app() -> FastAPI:
    app_config = config.AppConfig()
    # db.create_database(
    #     [
    #         health_models,
    #         item_models,
    #         student_models,
    #         teacher_models,
    #         textbook_models,
    #         course_models,
    #     ]
    # )
    # db.create_database(
    #     sum(
    #         [
    #             example.domain_models,
    #             school.domain_models,
    #         ],
    #         [],
    #     )
    # )
    prepare_db()

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
        routers = [
            iam_router,
            example.domain_router,
            school.domain_router,
        ]
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

    from mainapp.core.admin import admin, add_admin_views
    admin = add_admin_views(admin, school.domain_adminviews)
    admin.mount_to(app)

    logging.config.fileConfig("logging.conf", disable_existing_loggers=False,)
    log_level = os.getenv("APP_PROFILE", os.getenv("LOG_LEVEL", "INFO")).upper()
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)

    return app

app = create_app()
