from autologging import logged
from fastapi import FastAPI, APIRouter, Depends
import mainapp.core.config as core_config


@logged
def include_routers_by_config(
    app: FastAPI,
    routers: list[APIRouter],
    app_config: core_config.AppConfig = Depends(core_config.AppConfig),
) -> FastAPI:

    for router in routers:
        app.include_router(router)

    return app
