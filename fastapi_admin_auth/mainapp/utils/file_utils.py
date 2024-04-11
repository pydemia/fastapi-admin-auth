import os
import pathlib
from glob import glob
from pathlib import Path, PosixPath

import aiofiles
from fastapi import File, UploadFile

__all__ = [
    "remove_files_by_pattern",
]


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


# TODO: UploadFile list에서 filename list로 변경
async def extract_not_supported_embedding_file_extensions(
    file_list: list[UploadFile] = File(...),
) -> set:
    supported_file_ext: str = [
        # text
        ".txt",
        # pdf
        ".pdf",
        # 한글
        ".hwp",
        ".hwpx",
        # 압축파일
        ".zip",
        # word
        ".doc",
        ".docx",
        # excel
        ".xls",
        ".xlsx",
        ".csv",
        ".htm",
        ".xlt",
        ".xltx",
        ".xlsm",
        ".xlsb",
        ".xltm",
        ".xml",
        ".dif",
        ".slk",
        ".xlam",
        ".xla",
        ".ods",
        # presentation
        ".ppt",
        ".pptx",
        ".potx",
        ".pot",
        ".odp",
        ".pps",
        ".ppsx",
        ".pptm",
        ".potm",
        ".ppsm",
    ]

    not_supported_embedding_file_extension_set = set()
    for file in file_list:
        file_ext = pathlib.Path(file.filename).suffix
        if file_ext not in supported_file_ext:
            not_supported_embedding_file_extension_set.add(file_ext)
    return not_supported_embedding_file_extension_set


async def asave_file(dest_file_path: PosixPath, file: UploadFile) -> None:
    if not Path(dest_file_path).exists():
        Path(dest_file_path).mkdir(parents=True)

    async with aiofiles.open(dest_file_path / file.filename, "wb") as f:
        for i in iter(lambda: file.file.read(1024 * 1024 * 64), b""):
            await f.write(i)
