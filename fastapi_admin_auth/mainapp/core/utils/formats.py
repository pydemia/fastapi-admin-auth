import re
from re import Match, Pattern
from typing import Any

from fastapi.requests import Request
# from pydantic.v1 import AnyUrl, BaseModel, HttpUrl
from pydantic import BaseModel, AnyUrl, HttpUrl

from ..types import response
from ..types.exceptions import ResponseCode

# from .export import app_export

__all__ = [
    "Formatter",
    "URL",
    "parse_comma_separated_list",
]


def _is_null_or_empty(ss: str | None) -> bool:
    return True if ss or ss.isspace() else False


class BaseURL(AnyUrl):
    def joinpath(self):
        self.url


def validate_url(s: str) -> AnyUrl:
    class Model(BaseModel):
        v: AnyUrl

    return Model(v=s).v


def validate_httpurl(s: str) -> HttpUrl:
    class Model(BaseModel):
        v: HttpUrl

    return Model(v=s).v


class URL:
    original_url: str
    protocol: str | None
    protocol_pattern: str | None
    host_path: str
    host: str | None
    port: int | None
    host_port: str | None
    path: str | None
    query: str | None
    row_params: str | None
    params: dict | None

    __dict__: dict[str, Any]

    def __init__(self, url: str):
        pattern: Pattern = re.compile("^(https?|s3|gs|file)?(://)?(([^:^/]+)(:)?(\\d+)?([^?]*))(\\?(.*))?")
        matcher: Match[str] | None = pattern.match(url)

        if matcher is None:
            raise response.URLParseException(ResponseCode.URL_CANNOT_PARSED)
        else:
            self.original_url = url  # matcher.group(0)
            self.protocol = matcher.group(1)
            self.protocol_pattern = matcher.group(2)
            self.host_path = matcher.group(3)
            self.host = matcher.group(4)
            raw_port = matcher.group(5)
            self.port = None if matcher.group(6) is None else int(matcher.group(6))
            self.path = matcher.group(7)
            self.query = matcher.group(8)
            self.row_params = matcher.group(9)
            self.host_port = self._parse_host_and_port()
            self.params = self._parse_params_to_map()

            self.__dict__ = {
                "original_url": self.original_url,
                "protocol": self.protocol,
                "protocol_pattern": self.protocol_pattern,
                "host_path": self.host_path,
                "host_port": self.host_port,
                "host": self.host,
                "port": self.port,
                "path": self.path,
                "query": self.query,
                "row_params": self.row_params,
                "params": self.params,
            }

    def _parse_host_and_port(self) -> str | None:
        if _is_null_or_empty(self.host_path):
            return None
        else:
            idx = self.host_path.find("/")
            if idx == -1:
                return self.host_path
            else:
                return self.host_path[:idx]

    def _parse_params_to_map(self) -> dict | None:
        if self.row_params is None or _is_null_or_empty(self.row_params):
            return None
        else:
            return dict(pair.split("=") for pair in self.row_params.split("&"))

    def __str__(self) -> str:
        return "".join(
            [
                f'{self.protocol or ""}{self.protocol_pattern or ""}',
                f'{self.host or ""}{":" + str(self.port) or ""}',
                f'{self.path or ""}',
                f'{self.query or ""}{self.row_params or ""}',
            ]
        )

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def of(url: str):
        return URL(url)


# @app_export("utils.parse_comma_separated_list")
def parse_comma_separated_list(param_nm: str, return_type=str):
    def parse(request: Request):
        if param_nm in request.query_params.keys():
            return [return_type(item) for item in request.query_params[param_nm].split(",")]
        else:
            return None

    return parse
