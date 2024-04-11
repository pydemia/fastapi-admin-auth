"""Database module."""

from typing import Any

# import pandas as pd

from sqlalchemy.ext.declarative import declarative_base
# from langchain_community.embeddings import HuggingFaceEmbeddings

# from ..core.config import DBConfig

__all__ = [
    "Base",
    "RedisDataBase",
    "Database",
]

Base = declarative_base()

from sqlalchemy.orm import declarative_base


# Base = declarative_base()
# engine = create_engine(
#     "sqlite:///example.db",
#     connect_args={"check_same_thread": False},
# )


# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True)
#     name = Column(String)


# Base.metadata.create_all(engine)  # Create tables

# @inject
# class RedisDataBase:
#     def __init__(
#             self,
#             redis_config: RedisConfig = Provide["redis_config"],
#             ) -> None:
    
#         self.redis_config = redis_config
#         self.pool = redis.ConnectionPool(host=self.redis_config.host,
#                                          port=self.redis_config.port,
#                                          db=self.redis_config.db,
#                                          password=self.redis_config.password)

#     def session(self):
#         session = redis.Redis(connection_pool=self.pool,
#                               charset=self.redis_config.charset,
#                               decode_responses=self.redis_config.decode_responses)
#         return session

    # @contextmanager
    # def session(self):
    #     session = redis.Redis(host=self.redis_config.host,
    #                           password=self.redis_config.password,
    #                           port=self.redis_config.port,
    #                           db=self.redis_config.db,
    #                           charset=self.redis_config.charset,
    #                           decode_responses=self.redis_config.decode_responses)
    #
    #     try:
    #         yield session
    #     finally:
    #         session.close()

# @inject
# class Database:
#     def __init__(
#             self,
#             db_config: DBConfig = Provide["db_config"],
#             ) -> None:
#     # def __init__(self, db_config: Dict[str, Any]) -> None:
#         """
#         """
#         db_config_dict = db_config.dict(by_alias=False)
#         db_extra_config_dict = {
#             f"database.{k}": v for k, v in db_config_dict.items()
#             if k in db_config.extra_fields
#         }
#         db_extra_config_dict["database.url"] = 'mysql+pymysql://{username}:{password}@{host}:{port}/{dbname}'.format(
#             username=db_config.username,
#             password=db_config.password,
#             host=db_config.host,
#             port=db_config.port,
#             dbname=db_config.dbname,
#         )

#         # dotted = pd.json_normalize(db_config, sep=".").to_dict(orient='records')[0]
#         # dotted['database.url'] = 'mysql+pymysql://{username}:{password}@{host}:{port}/{dbname}'.format(
#         #     username=os.getenv("DATABASE__USERNAME", os.getenv("SYSTEMDB__USERNAME", dotted.pop("database.username", None))),
#         #     password=os.getenv("DATABASE__PASSWORD", os.getenv("SYSTEMDB__PASSWORD", dotted.pop("database.password", None))),
#         #     host=os.getenv("SYSTEMDB__HOST", os.getenv("DATABASE__HOST", dotted.pop("database.host", None))),
#         #     port=os.getenv("SYSTEMDB__PORT", os.getenv("DATABASE__PORT", dotted.pop("database.port", None))),
#         #     dbname=os.getenv("SYSTEMDB__DBNAME", os.getenv("DATABASE__DBNAME", dotted.pop("database.dbname", None))),
#         # )
#         # self._engine = engine_from_config(dotted, prefix="database.")
#         self._engine = engine_from_config(db_extra_config_dict, prefix="database.")
#         self._session_factory = orm.scoped_session(
#             orm.sessionmaker(
#                 autocommit=False,
#                 autoflush=False,
#                 bind=self._engine,
#             ),
#         )

#     def create_database(self) -> None:
#         """
#         """
#         try:
#             Base.metadata.create_all(bind=self._engine)
#         except Exception as e:
#             raise e

#     # def migration(self, template_dir: Path = None) -> None:
#     #     """
#     #     """
#     #     try:
#     #         def mig_templates():
#     #             import os
#     #             # from .models import CustomTemplateList
#     #             # from .crud import CustomTemplateListRepository
#     #             # from ..types.enums.nodes import TemplateType, ShareScope

#     #             custom_template_list = template_dir.glob("**/*.py")
#     #             for path in custom_template_list:
#     #                 with open(path, "r") as f:
#     #                     line_skip = f.readline()
#     #                     line_skip = f.readline()
#     #                     subject = f.readline().replace("- Subject:","").strip()
#     #                     description = f.readline().replace("- Description:","").strip()
#     #                     line_skip = f.readline()
#     #                     code = f.read()
#     #                 custom_template = CustomTemplateList()
#     #                 custom_template.template_id = path.stem
#     #                 custom_template.template_type = int(TemplateType.TEMPLATE)
#     #                 custom_template.subject = subject
#     #                 custom_template.description = description
#     #                 custom_template.default_yn = True
#     #                 custom_template.share_scope = int(ShareScope.GLOBAL)
#     #                 custom_template.project_id = 1
#     #                 custom_template.code = code
#     #                 custom_template.create_user = "system"
#     #                 custom_template.update_user = "system"
#     #                 custom_template.use_yn = True

#     #                 repo = CustomTemplateListRepository(self._session_factory)
#     #                 repo.add_or_update(custom_template)
#     #         mig_templates()

#     #     except Exception as e:
#     #         raise e

#     @contextmanager
#     def session(self) -> Callable[..., ContextManager[Session]]:
#         """
#         """
#         session: Session = self._session_factory()
#         try:
#             yield session
#         except Exception:
#             session.rollback()
#             raise
#         finally:
#             session.close()

## pagination.py


# from sqlalchemy.orm.query import Query
import sqlalchemy
from fastapi import Query
from pydantic import BaseModel
from sqlalchemy_filters import apply_pagination, apply_sort

__all__ = [
    "PageMetadata",
    "Page",
    "PageableParams",
    "pageable_params",
    "apply_pageable_params",
    "apply_sort_params",
]


class PageMetadata(BaseModel):
    number: int
    size: int
    totalElements: int
    totalPages: int


class Page(BaseModel):
    content: Any
    pageMetadata: PageMetadata

    def __init__(
        self,
        content: Any = None,
        page_number: int = None,
        page_size: int = None,
        total_results: int = None,
        num_pages: int = None,
    ):
        pageMetadata = PageMetadata(
            number=page_number,
            size=page_size,
            totalElements=total_results,
            totalPages=num_pages,
        )

        super().__init__(
            content=content,
            pageMetadata=pageMetadata,
        )

        # self.content = content
        # self.pageMetadata = pageMetadata


class PageableParams(BaseModel):
    page: int = 1
    size: int
    # limit: int
    # offset: int
    sort: list[str]
    # page: int = 1
    # size: int = 10
    # limit: int = 50
    # offset: int = 100
    # sort: List[str] = Query(
    #     ["model_version:desc"],
    # )


async def pageable_params(
    page: int = 1,
    size: int = 10,
    # limit: int = 50,
    # offset: int = 100,
    sort: list[str] = Query(
        [],
    ),
    # ) -> Dict[str, Any]:
) -> PageableParams:
    # return locals()
    return PageableParams(**locals())


def apply_pageable_params(
    query: sqlalchemy.orm.query.Query,
    pageable_params: PageableParams,
) -> Page:
    if pageable_params.sort:
        query = apply_sort_params(query, pageable_params.sort)

    query, pagination = apply_pagination(
        query,
        page_number=pageable_params.page,
        page_size=pageable_params.size,
    )
    page_number, page_size, num_pages, total_results = pagination

    return Page(
        content=query.all(),
        page_number=page_number,
        page_size=page_size,
        total_results=total_results,
        num_pages=num_pages,
    )


def _gen_sort_spec(sort_param):
    return {
        "model": "ModelDeployable",
        "field": sort_param[0],
        "direction": sort_param[1],
    }


def apply_sort_params(
    query: sqlalchemy.orm.query.Query,
    sort: list[str],
) -> sqlalchemy.orm.query.Query:
    sort_params = [s.split(":") for s in sort]
    sort_spec = [_gen_sort_spec(s) for s in sort_params]
    # sort_spec = [
    #     {"model": "ModelDeployable", "field": "name", "direction": "asc"},
    #     {"model": "ModelDeployable", "field": "id", "direction": "desc"},
    # ]
    return apply_sort(query, sort_spec)


# class Page:

#     page: int
#     size: int
#     number: int
#     is_first: bool
#     is_last: bool
#     has_previous: bool
#     has_next: bool
#     has_content: bool
#     total_elements: int
#     total_pages: int = 10
#     sort: str
#     direction: bool = True
#     number_of_elements: int
#     content: list()

#     @classmethod
#     def paginate(cls, content):
#         cls.content = content
#         cls.number = cls.page * cls.size + 1
#         cls.number_of_elements = len(content)
#         cls.has_content = True if cls.number_of_elements > 0 else False
#         cls.is_first = True if cls.page == 0 else False
#         cls.is_last = True if cls.page + 1 == cls.total_pages else False

#         response = dict()
#         response["content"] = cls.content
#         response["size"] = cls.size
#         response["number"] = cls.number
#         response["numberOfElements"] = cls.number_of_elements
#         response["hasContent"] = cls.has_content
#         # response["first"] = True if page_request.page == 0 else False
#         # response["last"] = True if page_request.page + 1 == page_request.total_pages else False
#         return response

#     @classmethod
#     def page_request(cls, page, size, sort, direction):
#         cls.page = page
#         cls.size = size
#         cls.sort = sort
#         cls.direction = direction
#         return cls


## query_utils.py
from typing import List, Any

from sqlalchemy_filters import apply_filters


__all__ = [
    "apply_nullable_filters",
]


def apply_nullable_filters(query, filter_spec: List):
    return apply_filters(
        query,
        filter(lambda x: x.get("value", None) is not None, filter_spec),
    )

