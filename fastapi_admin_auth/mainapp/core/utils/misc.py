from typing import Dict, Union, List
import ast
import json
import datetime as dt
from pathlib import Path, PurePath

from httpx import URL


__all__ = [
    "get_datetime",
    "error_parser",
    "find_pkg_rootpath",
    "joinpaths",
    "build_url",
    "decode_cellmsg",
    "dt_to_timemilis",
    "remove_files_by_pattern",
]


def get_datetime():
    return dt.datetime.now()


def error_parser(err: Exception):
    err_str = str(err)
    target_str = "HTTP response body: "
    try:
        target_idx = err_str.rindex(target_str) + len(target_str)
    except ValueError:
        target_idx = 0

    try:
        return json.loads(err_str[target_idx:])
    except json.decoder.JSONDecodeError:
        return err_str[target_idx:]

def find_pkg_rootpath() -> PurePath:
    dir_depth = len(__name__.split("."))
    path = PurePath(__file__)
    for _ in range(dir_depth):
        path = path.parent
    return path


def joinpaths(*paths: str) -> str:
    path0, *subpaths = paths
    return Path(path0).joinpath(*[p.lstrip("/") for p in subpaths]).as_posix()

def build_url(url: URL, *paths: str, **kwargs) -> URL:
    return URL(
        url,
        path=joinpaths(url.path, *paths),
        **kwargs,
    )


def decode_cellmsg(res: Union[str, List[str]]):
    if isinstance(res, str):
        res = [res]
    msg = ["\n".join(m) if isinstance(m, list) else m for m in res]
    # msg = [ast.literal_eval(f"b'''{m}'''").decode() for m in res]
    return '\n'.join(msg)
    # return msg

def filter_dict(d: Dict):
    return {k: v for k, v in d.items() if v is not None}


def dt_to_timemilis(time: dt.datetime):
    return round(time.timestamp() * 1000)


def remove_files_by_pattern(file_pattern: str) -> None:
    """패턴에 맞는 파일 삭제
    Args:
        file_pattern
    Returns:
    """
    file_list = glob(file_pattern)
    for f in file_list:
        try:
            os.remove(f)
        except FileNotFoundError:
            # pass exception
            pass

def get_comment_char(language):
    if language == "python":
        return "#"
    elif language == "java":
        return "//"
    elif language == "javascript":
        return "//"
    elif language == "go":
        return "//"
    elif language == "c++":
        return "//"
    else:
        return "#"