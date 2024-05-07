from typing import Any
from .models import Item
from fastapi import Depends
# from .crud import (
#     get_items_all,
#     get_items_by_ids,
#     get_items_by_range,
#     get_by_id,
#     create_item,
#     update_item,
#     delete_item,
# )

# get_items_all
# get_items_by_ids
# get_items_by_range
# get_by_id
# create_item
# update_item
# delete_item
from mainapp.core.types.exceptions import HandledException, ResponseCode
from .crud import ItemCRUD


class ItemService:
    def __init__(self):
        pass

    def __call__(
        self,
        crud: ItemCRUD = Depends(ItemCRUD()),
    ):
        self.item_crud = crud
        return self


    def add_new_item(
        self,
        item: dict[str, Any] | Item,
    ) -> Item:
        if isinstance(item, dict):
            item = Item(
                name=item["name"],
                description=item.get("description"),
            )
        item = self.item_crud.create(item)
        return item


    def add_new_items(
        self,
        item_list: list[dict[str, Any] | Item],
    ) -> list[Item]:
        items = [self.add_new_item(item) for item in item_list]
        return items


    def get_item(
        self,
        id_or_name_or_entity: int | str | Item,
    ) -> Item | None:
        if isinstance(id_or_name_or_entity, int):
            item = self.item_crud.get_by_id(id_or_name_or_entity)
        elif isinstance(id_or_name_or_entity, str):
            item = self.item_crud.get_by_name(id_or_name_or_entity)
        elif isinstance(id_or_name_or_entity, Item):
            item = self.item_crud.get_by_id(id_or_name_or_entity.id)
        else:
            raise HandledException(ResponseCode.ENTITY_ID_INVALID)

        return item


    def get_items_all(
        self,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Item | None]:
        if page:
            items = self.item_crud.gets_by_range(page=1)
        else:
            items = self.item_crud.get_all()
        return items
    
    def update_item_description(
        self,
        name: str,
        description: str,
    ) -> Item:
        item = self.get_item(name)
        if not item:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)
        
        item.description = description
        item = self.item_crud.update(item)
        return item


    def update_item(
        self,
        item_id: int,
        new_item: Item,
    ) -> Item:
        old_item: Item | None = self.item_crud.get_by_id(item_id)
        if not old_item:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)

        old_item.name = new_item.name
        old_item.description = new_item.description
        item = self.item_crud.update(old_item)

        return item


    def delete_item(
        self,
        id_or_name: str,
    ) -> bool:
        item = self.get_item(id_or_name)
        if not item:
            raise HandledException(ResponseCode.ENTITY_NOT_FOUND)

        return self.item_crud.delete(item)
