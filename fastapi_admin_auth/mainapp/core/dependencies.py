from types import ModuleType
from autologging import logged
from fastapi import FastAPI, APIRouter, Depends
import mainapp.core.config as core_config


from mainapp.core.health.routes import router as health_router
from mainapp.core.iam.routes import router as iam_router

from starlette_admin.views import BaseView
from mainapp.core.admin import get_admin, add_admin_views


@logged
def include_routers_by_config(
    app: FastAPI,
    routers: list[APIRouter],
    app_config: core_config.AppConfig = Depends(core_config.AppConfig),
) -> FastAPI:

    for router in routers:
        app.include_router(router)

    return app

@logged
def add_admin_view_by_config(
    app: FastAPI,
    admin_views: list[BaseView],
    app_config: core_config.AppConfig = Depends(core_config.AppConfig),
) -> FastAPI:

    # for admin_view in admin_views:
    admin = get_admin()
    app_admin = add_admin_views(admin, admin_views)
    app_admin.mount_to(app)

    return app


@logged
def mount_domains(
    app: FastAPI,
    modules: list[str | ModuleType]
) -> FastAPI:

    from importlib import import_module
    
    modules = [
        m
        if isinstance(modules, ModuleType)
        else import_module(f'.{m}', 'mainapp.domains')
        for m in modules
    ]

    app = include_routers_by_config(
        app,
        routers=[health_router, iam_router] + [
            m.domain_router for m in modules if getattr(m, 'domain_router')
        ],
    )
    app = add_admin_view_by_config(
        app,
        admin_views=sum([
            m.domain_adminviews for m in modules if getattr(m, 'domain_adminviews')
        ], []),
    )

    return app
