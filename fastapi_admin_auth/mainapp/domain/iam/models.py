from sqlmodel import SQLModel, Field, Relationship
import datetime as dt
from mainapp.core.types.common.fields import TimestampTZField


# TODO: In case of using SSO, OAuth;
# the app doesn't have any user info, but only using it from remote?


class UserGroupLink(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    group_id: int = Field(foreign_key="group.id")
    # user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    # group_id: int | None = Field(default=None, foreign_key="group.id", primary_key=True)


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    username: str
    password: str
    last_login: dt.datetime = TimestampTZField
    is_superuser: bool = False
    first_name: str
    last_name: str
    email: str
    is_staff: bool = False
    is_active: bool = True
    data_joined: dt.datetime = TimestampTZField
    groups: list["Group"] = Relationship(
        back_populates="users",
        link_model=UserGroupLink,
    )

class Group(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    description: str | None = None
    users: list["User"] = Relationship(
        back_populates="groups",
        link_modellink_model=UserGroupLink,
    )

