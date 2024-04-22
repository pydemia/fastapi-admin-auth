from typing import Iterable
from fastapi import Depends
from sqlmodel import select, col
from mainapp.core.database import db, Session

from .models import Textbook


class TextbookCRUD:
    def __init__(self):
        pass

    def __call__(
        self,
        session: Session = Depends(db.get_session),
    ):
        self.session = session
        return self

    def get_textbooks_all(
        self,
    ) -> list[Textbook | None]:    

        session = self.session
        stmt = select(Textbook)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_textbooks_by_range(
        self,
        page: int = 0,
        page_size: int = 10,
        order_by_asc: bool = True,
    ) -> list[Textbook | None]:

        session = self.session
        stmt = select(Textbook)
        if order_by_asc:
            stmt.order_by(col(Textbook.id).asc())
        else:
            stmt.order_by(col(Textbook.id).desc())
        stmt = stmt.offset(page_size * page)
        stmt = stmt.limit(page_size)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_textbooks_by_ids(
        self,
        ids: Iterable,
    ) -> list[Textbook | None]:

        session = self.session
        stmt = select(Textbook).where(Textbook.id in ids)
        stmt = session.exec(stmt)
        return stmt.all()


    def get_textbook_by_id(
        self,
        id,
    ) -> Textbook | None:

        session = self.session
        stmt = select(Textbook).where(Textbook.id == id)
        stmt = session.exec(stmt)
        return stmt.first()

    def get_textbook_by_name(
        self,
        name: str,
    ) -> Textbook | None:

        session = self.session
        stmt = select(Textbook).where(Textbook.name == name)
        stmt = session.exec(stmt)
        return stmt.first()

    def create_textbook(
        self,
        textbook: Textbook,
    ) -> Textbook:

        session = self.session
        session.add(textbook)
        session.commit()
        session.refresh(textbook)
        return textbook


    def get_or_create_textbook(
        self,
        name: str,
    ) -> Textbook:
        textbook: Textbook | None = self.get_textbook_by_name(
            name=name
        )
        if textbook:
            return textbook
        else:
            textbook = Textbook(name=name)
            textbook = self.create_textbook(textbook)
            return textbook


    def update_textbook(
        self,
        textbook: Textbook,
    ) -> Textbook:

        session = self.session
        session.add(textbook)
        session.commit()
        session.refresh(textbook)
        return textbook

    def delete_textbook(
        self,
        textbook: Textbook,
    ) -> None:
        session = self.session
        session.delete(textbook)
        session.commit()
