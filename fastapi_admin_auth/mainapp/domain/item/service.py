from .models import Item
from .crud import (
    get_items_all,
    get_items_by_ids,
    get_items_by_range,
    get_item_by_id,
    create_item,
    update_item,
    delete_item,
)

get_items_all
get_items_by_ids
get_items_by_range
get_item_by_id
create_item
update_item
delete_item
def get_item_by_id(item_id: int) -> Item:
    return Item(id=item_id)

