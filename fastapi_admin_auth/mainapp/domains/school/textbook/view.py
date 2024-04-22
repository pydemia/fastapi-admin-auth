from fastapi import APIRouter, Depends
# from mainapp.core.database import Session
from mainapp.core.exception_routers import HandledExceptionLoggingRoute
from mainapp.core.types.schema.response import CommonResponse
from .models import Textbook
from .service import TextbookService
from .schema import TextbookRequest


router = APIRouter(
    prefix="/textbooks",
    tags=["school/textbooks"],
    route_class=HandledExceptionLoggingRoute,
)


@router.get("")
async def get_textbooks(
    name: str | None = None,
    service: TextbookService = Depends(TextbookService()),
):
    if name:
        textbook_or_textbooks = service.get_textbook(name)
    else:
        textbook_or_textbooks = service.get_textbooks_all()
    return CommonResponse(data=textbook_or_textbooks)


@router.post("")
async def add_textbook(
    body: TextbookRequest,
    service: TextbookService = Depends(TextbookService()),
    ):
    textbook: Textbook = service.add_new_textbook(
        textbook={
            "name": body.name,
            "description": body.description,
        },
    )
    return CommonResponse(data=textbook)


@router.get("/{textbook_id}")
async def get_textbook_by_id(
    textbook_id: int,
    service: TextbookService = Depends(TextbookService()),
):
    textbook = service.get_textbook(textbook_id)
    return CommonResponse(data=textbook)


@router.put("/{textbook_id}")
async def update_textbook(
    textbook_id: int,
    body: TextbookRequest,
    service: TextbookService = Depends(TextbookService()),
):
    
    textbook = service.update_textbook(textbook_id, body)
    return CommonResponse(data=textbook)


@router.delete("/{textbook_id}")
async def delete_textbook(
    textbook_id: int,
    service: TextbookService = Depends(TextbookService()),
):
    is_deleted = service.delete_textbook(textbook_id)
    return CommonResponse(
        data={
            "id": textbook_id,
            "is_deleted": is_deleted,
        }
    )
