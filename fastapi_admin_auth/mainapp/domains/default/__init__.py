from fastapi import APIRouter
from mainapp.core.exception_routers import HandledExceptionLoggingRoute

from .health.view import router as health_router
from .item.view import router as item_router

router = APIRouter(
    prefix="/default",
    route_class=HandledExceptionLoggingRoute,
)

router.include_router(health_router)
router.include_router(item_router)
