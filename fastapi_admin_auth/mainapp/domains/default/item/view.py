from fastapi import APIRouter, Depends
# from mainapp.core.database import Session
from mainapp.core.exception_routers import HandledExceptionLoggingRoute
from mainapp.core.types.schema.response import CommonResponse
from .models import Item
from .service import ItemService
from .schema import ItemRequest

router = APIRouter(
    prefix="/items",
    tags=["items"],
    route_class=HandledExceptionLoggingRoute,
)


@router.get("")
async def get_items(
    name: str | None = None,
    service: ItemService = Depends(ItemService()),
):
    if name:
        item_or_items = service.get_item(name)
    else:
        item_or_items = service.get_items_all()
    return CommonResponse(data=item_or_items)


@router.post("")
async def add_item(
    body: ItemRequest,
    service: ItemService = Depends(ItemService()),
    ):
    item: Item = service.add_new_item(
        item={
            "name": body.name,
            "description": body.description,
        },
    )
    return CommonResponse(data=item)


@router.get("/{item_id}")
async def get_item_by_id(
    item_id: int,
    service: ItemService = Depends(ItemService()),
):
    item = service.get_item(item_id)
    return CommonResponse(data=item)


@router.put("/{item_id}")
async def update_item(
    item_id: int,
    body: ItemRequest,
    service: ItemService = Depends(ItemService()),
):
    
    item = service.update_item(item_id, body)
    return CommonResponse(data=item)


@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    service: ItemService = Depends(ItemService()),
):
    is_deleted = service.delete_item(item_id)
    return CommonResponse(
        data={
            "id": item_id,
            "is_deleted": is_deleted,
        }
    )
