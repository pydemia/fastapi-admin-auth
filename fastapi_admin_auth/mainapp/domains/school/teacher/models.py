

__all__ = [
    "Teacher",
]


from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from ..course.models import Course

class Teacher(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    firstname: str
    lastname: str
    description: str = Field("")

    courses: list["Course"] = Relationship(
            back_populates="teacher"
    )


# seed = [
#     (
#         Teacher,
#         [            
#             # Teacher(id=0, firstname="Daniel", lastname="Walker", description="teacher 0", courses=[0, 1]),
#             # Teacher(id=1, firstname="Sophia", lastname="Garcia", description="teacher 1", courses=[0, 2]),
#             # Teacher(id=2, firstname="Ethan", lastname="Miller", description="teacher 2", courses=[]),
#             Teacher(id=3, firstname="Charlotte", lastname="Wilson", description="teacher 3", courses=[2, 3]),
#             Teacher(id=4, firstname="Scarlett", lastname="Lewis", description="teacher a", courses=[4]),
#             Teacher(id=5, firstname="Audrey", lastname="Taylor", description="teacher b", courses=[1, 2, 4]),
#         ],
#     ),
# ]
