from typing import Iterable
from fastapi import Depends
from sqlmodel import select, col
from mainapp.core.database import db, Session

from .models import Item

def get_items_all(
    session: Session = Depends(db.get_session),
) -> list[Item | None]:    

    stmt = select(Item)
    stmt = session.exec(stmt)
    return stmt.all()


def get_items_by_range(
    page: int = 0,
    page_size: int = 10,
    order_by_asc=True,
    session: Session = Depends(db.get_session),
) -> list[Item | None]:

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
    ids: Iterable,
    session: Session = Depends(db.get_session),
) -> list[Item | None]:

    stmt = select(Item).where(Item.id in ids)
    stmt = session.exec(stmt)
    return stmt.all()


def get_item_by_id(
    id,
    session: Session = Depends(db.get_session),
) -> Item | None:

    stmt = select(Item).where(Item.id == id)
    stmt = session.exec(stmt)
    return stmt.first()

def add_item(
    item: Item,
    session: Session = Depends(db.get_session),
) -> Item:

    session.add(item)
    session.commit()
    session.refresh(item)
    return item

def update_item(
    item: Item,
    session: Session = Depends(db.get_session),
) -> Item:

    session.add(item)
    session.commit()
    session.refresh(item)
    return item

def delete_item(
    item: Item,
    session: Session = Depends(db.get_session),
) -> None:
    session.delete(item)
    session.commit()

