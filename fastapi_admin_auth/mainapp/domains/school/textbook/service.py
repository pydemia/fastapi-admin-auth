from typing import Any
from fastapi import Depends
# from .crud import (
#     get_textbooks_all,
#     get_textbooks_by_ids,
#     get_textbooks_by_range,
#     get_textbook_by_id,
#     create_textbook,
#     update_textbook,
#     delete_textbook,
# )

# get_textbooks_all
# get_textbooks_by_ids
# get_textbooks_by_range
# get_textbook_by_id
# create_textbook
# update_textbook
# delete_textbook
from mainapp.core.types.exceptions import HandledException, ResponseCode
from .models import Textbook
from .crud import TextbookCRUD


class TextbookService:
    def __init__(self):
        pass

    def __call__(
        self,
        crud: TextbookCRUD = Depends(TextbookCRUD()),
    ):
        self.textbook_crud = crud
        return self


    def add_new_textbook(
        self,
        textbook: dict[str, Any] | Textbook,
    ) -> Textbook:
        if isinstance(textbook, dict):
            textbook = Textbook(
                name=textbook["name"],
                description=textbook.get("description"),
            )
        textbook = self.textbook_crud.create(textbook)
        return textbook


    def add_new_textbooks(
        self,
        textbook_list: list[dict[str, Any] | Textbook],
    ) -> list[Textbook]:
        textbooks = [self.add_new_textbook(textbook) for textbook in textbook_list]
        return textbooks


    def get_textbook(
        self,
        id_or_name_or_entity: int | str | Textbook,
    ) -> Textbook | None:
        if isinstance(id_or_name_or_entity, int):
            textbook = self.textbook_crud.get_by_id(id_or_name_or_entity)
        elif isinstance(id_or_name_or_entity, str):
            textbook = self.textbook_crud.get_by_name(id_or_name_or_entity)
        elif isinstance(id_or_name_or_entity, Textbook):
            textbook = self.textbook_crud.get_by_id(id_or_name_or_entity.id)
        else:
            raise HandledException(ResponseCode.ENTITY_ID_INVALID)

        return textbook


    def get_textbooks_all(
        self,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Textbook | None]:
        if page:
            textbooks = self.textbook_crud.get_by_range(page=1)
        else:
            textbooks = self.textbook_crud.get_all()
        return textbooks
    
    def update_textbook_description(
        self,
        name: str,
        description: str,
    ) -> Textbook:
        textbook = self.get_textbook(name)
        if not textbook:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)
        
        textbook.description = description
        textbook = self.textbook_crud.update(textbook)
        return textbook


    def update_textbook(
        self,
        textbook_id: int,
        new_textbook: Textbook,
    ) -> Textbook:
        old_textbook: Textbook | None = self.textbook_crud.get_by_id(textbook_id)
        if not old_textbook:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)

        old_textbook.name = new_textbook.name
        old_textbook.description = new_textbook.description
        textbook = self.textbook_crud.update(old_textbook)

        return textbook


    def delete_textbook(
        self,
        id_or_name: str,
    ) -> bool:
        textbook = self.get_textbook(id_or_name)
        if not textbook:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)

        return self.textbook_crud.delete(textbook)
