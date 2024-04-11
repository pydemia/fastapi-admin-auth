
__all__ = [
    "get_namespace_nm",
    "get_storage_nm",
    "get_endpoint_nm",
    "cut_id",
]


def get_namespace_nm(project_id: int) -> str:
    return f"workflow-{project_id}"


def get_storage_nm(project_id: int) -> str:
    return f"workflow-{project_id}"


def get_endpoint_nm(project_id: int, model_id: str) -> str:
    return f'{get_namespace_nm(project_id)}-{model_id[:10]}'


def cut_id(id_string: str) -> str:
    return id_string.replace("-", "")[:10]
