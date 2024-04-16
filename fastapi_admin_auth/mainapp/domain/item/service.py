from .models import Item

def get_item_by_id(item_id: int) -> Item:
    return Item(id=item_id)