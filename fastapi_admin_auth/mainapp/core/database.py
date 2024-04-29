"""Database module."""

from typing import Any

# from sqlalchemy import orm
# from sqlalchemy.engine import engine_from_config
# from sqlalchemy.orm import Session
from sqlmodel import SQLModel, engine_from_config # create_engine
from sqlmodel import Session
from mainapp.core.config import DBConfig, db_config
import urllib.parse
from alembic.config import Config as AlembicConfig
from alembic import command as alembic_cmd



__all__ = [
    "Base",
    # "RedisDataBase",
    "Database",
]

# Base = declarative_base()


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

def flatten_json(y):
    out = {}

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


class Database:
    def __init__(
            self,
            db_config: DBConfig,
            ) -> None:
        """
        """
        db_config_dict = db_config.model_dump(by_alias=False)
        db_extra_config_dict = {
            f"database.{k}": v for k, v in db_config_dict.items()
            if (k in db_config.model_extra) and (v is not None)
        }
        if db_config.driver == "mysql":
            connector = "mysql+pymysql"
        elif db_config.driver == "postgresql":
            connector = "postgresql+psycopg"
        db_extra_config_dict["database.url"] = '{connector}://{username}:{password}@{host}:{port}/{dbname}'.format(
            connector=connector,
            username=db_config.username,
            password=urllib.parse.quote_plus(db_config.password),
            host=db_config.host,
            port=db_config.port,
            dbname=db_config.dbname,
        )
        self.db_url = db_extra_config_dict["database.url"]

        self.engine = engine_from_config(
            db_extra_config_dict,
            prefix="database.",
        )

    # @asynccontextmanager
    async def get_session(self):
        with Session(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
        ) as session:
            yield session
            # try:
            #     yield session
            # except Exception:
            #     session.rollback()
            # finally:
            #     session.close()

    def create_database(self, model_modules=[]) -> None:
        """
        Arguments
        ---------

            model_modules: List[module]
                This argument is not used internally,
                but It enforces importing ORM models of SQLModel before calling `create_all`.
        """
        try:
            # Base.metadata.create_all(bind=self._engine)
            SQLModel.metadata.create_all(self.engine)
        except Exception as e:
            raise e

    def apply_migration(self, alembic_config_filepath: str = "alembic.ini"):
        alembic_cfg = AlembicConfig(alembic_config_filepath)
        alembic_cfg.set_main_option("sqlalchemy.url", self.db_url)
        alembic_cmd.upgrade(alembic_cfg, "head")

    # def prepare(self,  model_modules=[], alembic_config_filepath: str = "alembic.ini"):
    #     self.create_database(model_modules)
    #     self.apply_migration(alembic_config_filepath=alembic_config_filepath)


## pagination.py

db = Database(db_config=db_config)

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

