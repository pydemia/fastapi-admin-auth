

__all__ = [
    "Item",
    "ItemModelView",
]

from sqlmodel import Field, SQLModel


class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str = Field("")

from starlette_admin.contrib.sqla import ModelView

ItemModelView = ModelView(Item, icon=None, label=None)
