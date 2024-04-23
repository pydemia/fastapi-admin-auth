# from fastapi import APIRouter
# from mainapp.core.exception_routers import HandledExceptionLoggingRoute

# from .health.routes import router as health_router
# from .item.routes import router as item_router

# router = APIRouter(
#     prefix="/default",
#     route_class=HandledExceptionLoggingRoute,
# )

# router.include_router(health_router)
# router.include_router(item_router)

from mainapp.core.domains import import_domain_components

router, admin_views, models = import_domain_components(__name__)
