from fastapi import APIRouter
from mainapp.core.exception_routers import HandledExceptionLoggingRoute
from mainapp.core.types.schema.response import CommonResponse
from dependency_injector.wiring import inject

router = APIRouter(
    prefix="/health",
    tags=["health"],
    route_class=HandledExceptionLoggingRoute,
)

@inject
@router.get(
    "/live",
    status_code=200,
    dependencies=None,
    # response_model=CommonResponse,
)
def is_live(
    # debug_service: DebugService = Depends(Provide[Container.debug_service])
):
    return CommonResponse(data="App is live")

@router.get(
    "/ready",
    status_code=200,
    dependencies=None,
    # response_model=CommonResponse,
)
def is_ready():
    return CommonResponse(data="App is ready")
