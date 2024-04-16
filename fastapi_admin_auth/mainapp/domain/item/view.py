from fastapi import APIRouter
# from mainapp.core.database import Session
from mainapp.core.exception_routers import HandledExceptionLoggingRoute
from mainapp.core.types.schema.response import CommonResponse

router = APIRouter(
    prefix="/items",
    tags=["items"],
    route_class=HandledExceptionLoggingRoute,
)

@router.get("/")
async def get_items():
    # return await db.query(Item).all()
    return CommonResponse(data=[])
