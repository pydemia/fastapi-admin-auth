from typing import Iterable
from fastapi import Depends
from sqlmodel import select, col
from mainapp.core.database import db, Session

from .models import Item


class ItemCRUD:
    def __init__(self):
        pass

    def __call__(
        self,
        session: Session = Depends(db.get_session),
    ):
        self.session = session
        return self

    def get_items_all(
        self,
    ) -> list[Item | None]:    

        session = self.session
        stmt = select(Item)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_items_by_range(
        self,
        page: int = 0,
        page_size: int = 10,
        order_by_asc: bool = True,
    ) -> list[Item | None]:

        session = self.session
        stmt = select(Item)
        if order_by_asc:
            stmt.order_by(col(Item.id).asc())
        else:
            stmt.order_by(col(Item.id).desc())
        stmt = stmt.offset(page_size * page)
        stmt = stmt.limit(page_size)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_items_by_ids(
        self,
        ids: Iterable,
    ) -> list[Item | None]:

        session = self.session
        stmt = select(Item).where(Item.id in ids)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_item_by_id(
        self,
        id,
    ) -> Item | None:

        session = self.session
        stmt = select(Item).where(Item.id == id)
        stmt = session.exec(stmt)
        return stmt.first()

    def get_item_by_name(
        self,
        name: str,
    ) -> Item | None:

        session = self.session
        stmt = select(Item).where(Item.name == name)
        stmt = session.exec(stmt)
        return stmt.first()

    def create_item(
        self,
        item: Item,
    ) -> Item:

        session = self.session
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


    def get_or_create_item(
        self,
        name: str,
    ) -> Item:
        item: Item | None = self.get_item_by_name(
            name=name
        )
        if item:
            return item
        else:
            item = Item(name=name)
            item = self.create_item(item)
            return item


    def update_item(
        self,
        item: Item,
    ) -> Item:

        session = self.session
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    def delete_item(
        self,
        item: Item,
    ) -> None:
        session = self.session
        session.delete(item)
        session.commit()
