from typing import Optional
import uuid
from datetime import datetime


__all__ = [
    "gen",
    "gen_node_id",
    "gen_endpoint_id",
    "gen_logtrace_id",
    "gen_transaction_id",
    "gen_model_id",
    "gen_version_tag",
    "gen_short",
    "gen_workflow_id",
    "gen_dataset_id",
    "gen_fileset_id",
    "gen_schedule_id",
    "gen_template_id",
    "gen_backup_id",
    "gen_restore_id",
    "gen_extension_node_id",
    "convert_int",
    "convert_str",
    "gen_short_uuid",
    "gen_code_req_id"
]


def gen() -> str:
    return str(uuid.uuid4())


def gen_node_id() -> str:
    node_id = gen().replace("-", "")
    splits = [node_id[i:i+4] for i in range(0, len(node_id), 4)]
    return "-".join(splits)


def gen_endpoint_id(uid: Optional[str] = None) -> str:
    return f"edp-{gen() if uid is None else uid}"


def gen_logtrace_id(uid: Optional[str] = None) -> str:
    return f"log-{gen() if uid is None else uid}"

def gen_transaction_id(uid: Optional[str] = None) -> str:
    return f"trn-{gen() if uid is None else uid}"

def gen_model_id(uid: Optional[str] = None) -> str:
    return f"mdl-{gen() if uid is None else uid}"


def gen_version_tag() -> str:
    return gen()[0:5]


def gen_short(l: int) -> str:
    return gen().replace("-", "")[0:l]


def gen_transaction_id(uid: Optional[str] = None) -> str:
    """Workflow ID 생성
    """
    return f"trn-{gen() if uid is None else uid}"


def gen_workflow_id(uid: Optional[str] = None) -> str:
    """Workflow ID 생성
    """
    return f"wfl-{gen() if uid is None else uid}"


def gen_workflow_id_int() -> int:
    """정수형 Workflow ID 생성
    """
    return int(datetime.now().strftime('%y%m%d%H%M%f'))


def gen_dataset_id(uid: Optional[str] = None) -> str:
    """Dataset ID 생성
    """
    return f"dst-{gen() if uid is None else uid}"


def gen_fileset_id(uid: Optional[str] = None) -> str:
    """Fileset ID 생성
    """
    return f"fst-{gen() if uid is None else uid}"


def gen_schedule_id(uid: Optional[str] = None) -> str:
    """Schedule ID 생성
    """
    return f"sch-{gen() if uid is None else uid}"


def gen_template_id(uid: Optional[str] = None) -> str:
    """Custom Template ID 생성
    """
    return f"cst-{gen() if uid is None else uid}"


def gen_extension_node_id(uid: Optional[str] = None) -> str:
    """Extension node ID 생성
    """
    return f"ext-{gen() if uid is None else uid}"


def gen_backup_id(uid: Optional[str] = None) -> str:
    """Backup ID 생성
    """
    return f"bak-{gen() if uid is None else uid}"


def gen_restore_id(uid: Optional[str] = None) -> str:
    """Restore ID 생성
    """
    return f"rst-{gen() if uid is None else uid}"


def convert_int(uid: str) -> int:
    """UUID를 int 형으로 변환
    """
    return uuid.UUID(uid[4:], version=4).int


def convert_str(uid: int) -> str:
    """int형 UUID를 UUID 형으로 변환
    """
    return str(uuid.UUID(int=uid, version=4))


def gen_short_uuid() -> str:
    """4자리 UUID 생성
    """
    return str(uuid.uuid4())[:4]


def gen_21_uuid() -> str:
    """21자리 UUID 생성
    """
    return str(uuid.uuid4())[:21]
def gen_prompt_uuid() -> str:
    return f"prompt-{gen()}"

def gen_code_req_id(uid: Optional[str] = None) -> str:
    """Code Req ID 생성
    """
    return f"code-req-{gen() if uid is None else uid}"


def gen_apikey() -> str:
    """APIKEY 생성
    """
    return f"{gen()[:25]}CRS"


def gen_activation_id() -> str:
    """Activation id 생성
    """
    return f"={gen()[:18]}"
