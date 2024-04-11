import os
from enum import Enum, unique
from functools import partial
from pathlib import PurePath
from typing import Any

import yaml
from autologging import logged
from pydantic import (
    BaseModel,
    BaseSettings,
    Extra,
    Field,
    ValidationError,
    root_validator,
    validator,
)
from pydantic.env_settings import SettingsSourceCallable

# from pydantic.v1 import (
#     BaseModel,
#     Field,
#     Extra,
#     root_validator,
#     validator,
#     ValidationError,
# )
# from pydantic.v1.fields import FieldInfo
# from pydantic_settings import (
#     BaseSettings,
#     EnvSettingsSource,
#     PydanticBaseSettingsSource,
# )
from ..enums import Locale

__all__ = [
    "ResponseCode",
]


def _find_rootpath() -> PurePath:
    dir_depth = len(__name__.split("."))
    path = PurePath(__file__)
    for _ in range(dir_depth):
        path = path.parent
    return path


def _yaml_config_settings_source(settings: BaseSettings, filepath: PurePath) -> dict[str, Any]:
    """A simple settings source that loads variables from a JSON file
    at the project's root.

    Here we happen to choose to use the `env_file_encoding` from Config
    when reading `config.json`
    """
    # encoding = settings.__config__.env_file_encoding
    # return json.loads(Path('config.json').read_text(encoding))
    try:
        with open(filepath) as f:
            config = yaml.load(f, Loader=yaml.Loader)
    except FileNotFoundError:
        with open(_find_rootpath().joinpath(filepath)) as f:
            config = yaml.load(f, Loader=yaml.Loader)
    return config


CODEMSG_FILEPATH = os.getenv("APP_CODE", "code.yaml")
APPCONF_FILEPATH = os.getenv("APP_CONFIG", "config.yaml")

_load_code_config = partial(
    _yaml_config_settings_source,
    filepath=CODEMSG_FILEPATH,
)
_load_app_config = partial(
    _yaml_config_settings_source,
    settings=None,
    filepath=APPCONF_FILEPATH,
)


class Message(BaseModel):
    ko: str
    en: str


DEFAULT_LOCALE = Locale.KO
try:
    LOCALE = Locale(_load_app_config().get("app", {"locale": "ko"}).get("locale", "ko"))
except Exception:
    LOCALE = DEFAULT_LOCALE


class Code(BaseModel):
    code: int = Field(ge=-99999, le=1, multiple_of=1)
    message: str

    @validator("message", pre=True, always=True, allow_reuse=True)
    def select_msg_by_locale(cls, v):
        msg = Message.parse_obj(v)
        return msg.__getattribute__(LOCALE.value)

    class Config:
        extra = Extra.ignore


class CodeMessage(BaseModel):
    field: str
    code: int
    message: str

    class Config:
        allow_mutation = False


# class LoadCodeYamlSettingsSource(EnvSettingsSource):
#     def prepare_field_value(
#         self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
#     ) -> Any:
#         """
#         A simple settings source that loads variables from a JSON file
#         at the project's root.

#         Here we happen to choose to use the `env_file_encoding` from Config
#         when reading `config.json`
#         """
#         # encoding = settings.__config__.env_file_encoding
#         # return json.loads(Path('config.json').read_text(encoding))
#         try:
#             filepath = os.getenv("APP_CODE", "code.yaml")
#             with open(filepath, "r") as f:
#                 config = yaml.load(f, Loader=yaml.Loader)
#         except FileNotFoundError:
#             with open(_find_rootpath().joinpath(filepath), "r") as f:
#                 config = yaml.load(f, Loader=yaml.Loader)
#         return config


@logged
class CodeMessages(BaseSettings):
    @root_validator(pre=True)
    def convert_dict2model(cls, values):
        try:
            new_values = {}
            for k, v in values.items():
                new_values.update({k: Code.parse_obj(v)})
                # return {k: Code.parse_obj(v) for k, v in values.items()}
            return new_values
        except ValidationError as e:
            cls.__log.warn(f"Failed to parse 'config.yaml' with FIELD '{k}': {v}")
            raise e

    class Config:
        extra = Extra.allow
        allow_mutation = False

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            return (
                init_settings,
                _load_code_config,
                env_settings,
                file_secret_settings,
            )

    # @classmethod
    # def settings_customise_sources(
    #     cls,
    #     settings_cls: Type[BaseSettings],
    #     init_settings: PydanticBaseSettingsSource,
    #     env_settings: PydanticBaseSettingsSource,
    #     dotenv_settings: PydanticBaseSettingsSource,
    #     file_secret_settings: PydanticBaseSettingsSource,
    # ) -> Tuple[PydanticBaseSettingsSource, ...]:
    #     return (LoadCodeYamlSettingsSource(settings_cls),)

    def find_by_code(self, code: int) -> CodeMessage | None:
        fields: dict[str, Code] = self.__dict__
        try:
            matched = [
                CodeMessage(field=k, code=v.code, message=v.message) for k, v in fields.items() if v.code == code
            ]
            return matched[0]
        except IndexError as e:
            self.__log.debug(
                f"nothing matched in 'CodeMessages' with code={code}",
            )
            self.__log.debug(e)
            return None

    def find_by_field(self, field: str) -> CodeMessage | None:
        fields: dict[str, Code] = self.__dict__
        try:
            matched = [CodeMessage(field=k, code=v.code, message=v.message) for k, v in fields.items() if k == field]
            return matched[0]
        except IndexError as e:
            self.__log.debug(
                f"nothing matched in 'CodeMessages' with field={field}",
            )
            self.__log.debug(e)
            return None


code_messages = CodeMessages()


@unique
class ResponseCode(Enum):
    # general(~)
    SUCCESS = (1, "성공")
    FAIL = (-1, "실패")
    UNDEFINED_ERROR = (-2, "정의되지 않은 오류입니다.")

    RESPONSECODE_NOT_SET = (-3, "ErrorResponse에 응답 코드가 정의되지 않았습니다.")
    INVALID_APP_CONFIG_ERROR = (-4, "Application의 Config 값에 문제가 있습니다.")

    # ENTITY_RUN_FAILED = (-10001, "Entity 실행에 실패하였습니다.")
    # ENTITY_NOT_FOUND = (-10002, "Entity를 찾을 수 없습니다.")
    # ENTITY_ALREADY_EXISTS = (-10003, "Entity가 이미 존재합니다.")
    # ENTITY_CANNOT_CREATED = (-10004, "Entity를 생성할 수 없습니다.")
    # ENTITY_CANNOT_UPDATED = (-10005, "Entity를 업데이트할 수 없습니다.")
    # ENTITY_CANNOT_DELETED = (-10006, "Entity를 삭제할 수 없습니다.")
    # ENTITY_ID_INVALID = (-10007, "Entity ID 값에 문제가 있습니다.")

    # Gateway & Account = (-1000 ~ 1099)
    EXPIRED_TOKEN = (-1002, "토큰이 만료되었습니다.")
    FORGERY_TOKEN = (-1003, "위변조된 토큰입니다.")
    NON_EXISTENT_ACCESS_KEY = (-1004, "존재하지 않는 인증키 입니다.")
    INVALID_PASSWORD = (-1005, "비밀번호가 일치하지 않습니다.")
    PAUSED_ACCOUNT = (-1006, "사용 정지된 계정입니다.")
    NON_EXISTENT_ID = (-1007, "로그인에 실패했습니다.")
    ID_ALREADY_EXISTS = (-1008, "이미 존재하는 ID 입니다.")
    DELETED_ID = (-1009, "삭제된 ID 입니다.")
    DO_NOT_HAVE_PERMISSION = (-1010, "권한이 없습니다.")
    WRONG_SORT_TYPE = (-1011, "잘못된 정렬 형식입니다.")
    INVALID_OLD_PASSWORD = (-1012, "기존 비밀번호가 일치하지 않습니다.")
    NEW_PWD_MUST_BE_DIFFERENT = (-1013, "새로운 비밀번호는 기존 비밀번호와 동일할 수 없습니다.")
    REDIS_SERVER_ERROR = (-1014, "캐시 서버 접속 실패")
    INVALID_PWD_REGEX = (-1015, "규칙에 어긋나는 비밀번호입니다.")
    INVALID_ID = (-1016, "존재하지 않는 ID입니다.")

    NON_EXISTENT_COM_CODE = (-1050, "존재하지 않는 COM CODE 입니다.")
    WRONG_CRITERIA_TYPE = (-1051, "잘못된 검색 기준값입니다.")

    KEY_GENERATION_ERROR = (-1060, "키 생성 중 에러가 발생했습니다.")
    INVALID_KEY = (-1061, "존재 하지 않는 키 입니다.")
    VERIFICATION_FAIL = (-1062, "공개키 인증을 실패 했습니다.")
    DUPLICATION_ERROR = (-1063, "이미 존재하는 키 정보 입니다.")
    INVALID_CLIENT_TYPE = (-1064, "잘못된 Client Type입니다.")

    # Utility error code  = (-1900 ~ -1999)
    MICRO_SERVICE_NO_AVAILABLE = (-1901, "해당 마이크로 서비스를 찾을 수 없습니다.")
    CONNECTION_ERROR = (-1902, "마이크로 서비스 연결에 문제가 발생했습니다.")

    # CORE  = (-2000 ~ -2999) -------------------------------------------------
    # Common Error = (-2000 ~ -2159)
    NOT_IMPLEMENTED = (-2000, "구현되지 않은 동작입니다.")
    NULL_VALUE_DETECTED = (-2001, "전달된 값이 없습니다.")
    INVALID_INPUT_VALUE = (-2002, "INPUT 값이 올바르지 않습니다.")
    INSUFFICIENT_INPUT = (-2003, "필수 값이 빠져 있습니다.")
    UNAUTHORIZED = (-2004, "접근 권한이 없습니다.")
    UNAUTHENTICATED = (-2005, "사용자 인증이 실패하였습니다.")
    METHOD_NOT_ALLOWED = (-2006, "허가되지 않은 요청입니다.")
    JSON_CANNOT_PARSED = (-2007, "Json Parsing 중 문제가 발생했습니다.")
    JSON_CANNOT_BUILDED = (-2008, "Json Build 중 문제가 발생했습니다.")
    YAML_CANNOT_PARSED = (-2009, "Yaml Parsing 중 문제가 발생했습니다.")
    YAML_CANNOT_BUILDED = (-2010, "Yaml Build 중 문제가 발생했습니다.")
    INVALID_NEGATIVE_VALUE = (-2011, "INPUT 값은 음수를 입력할 수 없습니다.")
    URL_CANNOT_PARSED = (-2012, "URL 값이 올바르지 않습니다.")
    INVALID_VALUE_IN_REQUEST = (-2013, "요청에 사용한 값이 올바르지 않습니다.")

    # graphql error  = (-2160 ~ -2199)
    GQL_UNDEFINED_ERROR = (-2160, "쿼리 중 정의되지 않은 오류가 발생했습니다.")

    # Value Error  = (-2200 ~ -2299)
    INVALID_ACCOUT_ID_FORMAT = (-2200, "잘못된 ACCOUNT_ID 형식입니다.")
    ACCOUT_ID_NOT_INT_FORMAT = (-2201, "ACCOUNT_ID는 숫자 값 형태이어야 합니다.")
    INVALID_INTEGER_STRING = (-2202, "잘못된 정수값 문자열입니다.")
    INVALID_FLOAT_STRING = (-2203, "잘못된 소수값 문자열입니다.")
    INVALID_FRAMEWORK_TYPE = (-2204, "잘못된 프레임워크 타입입니다.")
    INVALID_GPU_FRAMEWORK_TYPE = (-2205, "GPU를 사용할 수 없는 프레임워크 타입입니다.")
    INVALID_NAME_FORMAT = (-2206, "서비스 네임 형식이 올바르지 않습니다.")
    INVALID_CONCURRENT_FORMAT = (-2207, "Concurrent 형식이 올바르지 않습니다.")
    INVALID_CONTAINER_PORTS = (-2208, "Container Ports는 0 ~ 65535 사이의 정수만 입력할 수 있습니다.")

    # Kubernetes error code  = (-2300 ~ -2599)
    K8S_UNDEFINED_ERROR = (-2300, "Kubernetes 클러스터 요청 도중 정의되지 않은 문제가 발생했습니다.")
    K8S_CLIENT_IO_ERROR = (-2301, "Kubernetes 클러스터 요청 도중 IO 문제가 발생했습니다.")
    K8S_CLIENT_ACTION_ERROR = (-2302, "Kubernetes 클라이언트에서 문제가 발생했습니다.")
    K8S_CANNOT_START_CLIENT = (-2303, "Kubernetes 클라이언트 시작에 실패했습니다.")
    K8S_CANNOT_LOAD_CONFIG = (-2304, "Kubernetes Configuration을 읽을 수 없습니다.")
    K8S_MISSING_PROPERTIES = (-2305, "Kubernetes Property를 찾을 수 없습니다.")
    K8S_CANNOT_LOAD_PROPERTIES = (-2306, "Kubernetes 리소스 접근 권한이 없습니다.")
    K8S_UNAUTHORIZED = (-2307, "Kubernetes 클러스터 접근 권한이 없습니다.")
    NAMESPACE_NOT_FOUND = (-2308, "NAMESPACE를 찾을 수 없습니다.")
    NAMESPACE_ALREADY_EXISTS = (-2309, "이미 존재하는 Namespace입니다.")
    INVALID_NAMESPACE_FORMAT = (
        -2310,
        "Namespace의 형식이 올바르지 않습니다.\n(Namespace에는 알파벳, 숫자, '-'만 사용가능하며 시작과 끝이 알파벳 또는 숫자입니다.)",
    )
    K8S_SERVICE_NOT_FOUND = (-2311, "Kubernetes Service를 찾을 수 없습니다.")
    K8S_RESOURCE_NOT_FOUND = (-2316, "Kubernetes Resource를 찾을 수 없습니다.")
    K8S_INGRESS_PORT_NOT_FOUND = (-2317, "Ingress HTTP2 Port를 찾을 수 없습니다.")
    K8S_INGRESS_NODEPORT_IP_NOT_GIVEN = (
        -2318,
        "NodePort Type일 경우, `k8s.ingress.spec.nodePort.ip`에 IP를 명시해야 합니다.",
    )
    K8S_INGRESS_TYPE_NOT_SUPPORTED = (
        -2319,
        "Ingress Service Type이 지원하지 않는 형식입니다.[not in (LoadBalancer, NodePort)]",
    )
    K8S_CONFIG_SATOKEN_NOT_FOUND = (
        -2320,
        "serviceAccount Token(`k8s.serviceAccount.token`)을 찾을 수 없습니다."
        + "`k8s.isIntra=false` 일 때, 반드시 적절한 token을 부여해야 합니다.",
    )

    S3_CLIENT_ERROR = (-2700, "S3 Client 동작 중 문제가 발생했습니다.")
    S3_CLIENT_CANNOT_LIST_BUCKET = (-2700, "Bucket 조회 중 문제가 발생했습니다. Bucket을 조회할 수 없습니다.")
    S3_CLIENT_CANNOT_CREATE_BUCKET = (-2701, "Bucket 생성 중 문제가 발생했습니다. Bucket을 생성할 수 없습니다.")
    S3_CLIENT_CANNOT_DELETE_BUCKET = (-2702, "Bucket 삭제 중 문제가 발생했습니다. Bucket을 삭제할 수 없습니다.")
    S3_CLIENT_BUCKET_ALREADY_EXISTS = (-2703, "Bucket이 이미 존재합니다.")
    S3_CLIENT_BUCKET_NOT_FOUND = (-2704, "Bucket을 찾을 수 없습니다.")
    S3_CLIENT_UPLOAD_ERROR = (-2705, "Bucket에 File Upload 중 문제가 발생했습니다.")
    S3_CLIENT_MULTIPARTFILE_TO_FILE_IO_ERROR = (-2706, "MultipartFile을 처리하는 도중 문제가 발생했습니다.")
    S3_CLIENT_CANNOT_LIST_OBJECT = (-2707, "Object 조회 중 문제가 발생했습니다. Object를 조회할 수 없습니다.")
    S3_CLIENT_CANNOT_UPLOAD_OBJECT = (-2708, "Object Upload 중 문제가 발생했습니다. Object를 Upload할 수 없습니다.")
    S3_CLIENT_CANNOT_DELETE_OBJECT = (-2709, "Object 삭제 중 문제가 발생했습니다. Object를 삭제할 수 없습니다.")
    S3_CLIENT_OBJECT_NOT_FOUND = (-2709, "Object를 찾을 수 없습니다.")

    HARBOR_CLIENT_ERROR = (-2720, "Harbor Client 동작 중 문제가 발생했습니다.")
    HARBOR_CLIENT_USER_NOT_EXIST = (-2721, "Harbor User가 존재하지 않습니다.")
    HARBOR_CLIENT_USER_ALREADY_EXISTS = (-2722, "Harbor User가 이미 존재합니다.")
    HARBOR_CLIENT_CANNOT_CREATE_USER = (-2723, "Harbor User를 생성할 수 없습니다.")
    HARBOR_CLIENT_CANNOT_DELETE_USER = (-2724, "Harbor User를 삭제할 수 없습니다.")
    HARBOR_CLIENT_PROJECT_NOT_EXIST = (-2725, "Harbor Project가 존재하지 않습니다.")
    HARBOR_CLIENT_PROJECT_ALREADY_EXISTS = (-2726, "Harbor Project가 이미 존재합니다.")
    HARBOR_CLIENT_CANNOT_CREATE_PROJECT = (-2727, "Harbor Project를 생성할 수 없습니다.")
    HARBOR_CLIENT_CANNOT_DELETE_PROJECT = (-2728, "Harbor Project를 삭제할 수 없습니다.")

    CEPH_CLIENT_ERROR = (-2740, "Ceph Client 연결 중 문제가 발생했습니다.")
    CEPH_CLIENT_USER_NOT_EXIST = (-2741, "Ceph User가 존재하지 않습니다.")
    CEPH_CLIENT_USER_ALREADY_EXISTS = (-2742, "Ceph User가 이미 존재합니다.")

    # Etc.(Reserved) error code  = (-3900 ~ -3999)
    EXCEPTION_IN_TEST = (-3999, "예외 처리 테스트를 위한 항목입니다.")

    # RestClientException  = (-4000 ~ -4100)
    RESTCLIENT_CANNOT_LOAD_CACERT = (-4000, "ca.crt 를 로드하는 과정에서 문제가 발생하였습니다.")
    RESTCLIENT_CANNOT_GET_KEYSTORE = (-4001, "CA_KEYSTORE을 정의하는 도중 문제가 발생하였습니다.")
    RESTCLIENT_CANNOT_CREATE_SSLCONTEXT = (-4002, "SSL 접속 구성 중 문제가 발생하였습니다.")
    RESTCLIENT_CANNOT_PARSE_RESPONSE_CONTENT = (-4003, "Response의 Content를 가져오는 도중 문제가 발생하였습니다.")
    RESTCLIENT_WRONG_URI_FORMAT = (-4004, "URI 형식이 맞지 않습니다.")
    RESTCLIENT_REQUEST_ERROR = (-4005, "내부 RequestClient가 다른 API를 대상으로 요청 중 문제가 발생하였습니다.")

    # AsyncThreadPoolTaskException = (-9000 ~ -9099)
    ASYNC_TASK_UNEXPECTEDLY_CLOSED = (-9000, "비동기 작업이 비정상 종료되었습니다.")
    ASYNC_TASK_WATCH_PIPELINERUN_UNEXPECTEDLY_CLOSED = (
        -9001,
        "비동기 작업: Tekton PipelineRun Watch 작업이 비정상 종료되었습니다.",
    )
    ASYNC_TASK_WATCH_IFSVC_UNEXPECTEDLY_CLOSED = (
        -9002,
        "비동기 작업: InferenceService Watch 작업이 비정상 종료되었습니다.",
    )
    ASYNC_TASK_TIMEOUT = (-9003, "비동기 작업이 Timeout 되었습니다.")

    # AttributeConvertException = (-9100 ~ -9199)
    CANNOT_CONVERT_DB_ENTRY_TO_ATTRIBUTE = (-9100, "지원하지 않는 값이 입력되어 처리할 수 없습니다.")

    # LLM Model
    MODEL_NOT_FOUND = (-10001, "모델을 찾을 수 없습니다.")
    MODEL_NOT_SET = (-10002, "모델이 설정되지 않았습니다.")
    MODEL_NOT_SUPPORTED = (-10003, "해당 모델은 지원하지 않습니다.")
    MODEL_ALREADY_EXISTS = (-10004, "해당 모델은 이미 존재합니다.")
    MODEL_TYPE_NOT_SUPPORTED = (-10005, "해당 모델 타입은 지원하지 않습니다.")
    MODEL_TYPE_NOT_VALID = (-10006, "해당 모델 타입이 올바르지 않습니다.")
    MODEL_ENDPOINT_NOT_VALID = (-10007, "모델 API endpoint가 올바르지 않습니다.")
    MODEL_ENDPOINT_ERROR = (-10008, "모델 API ERROR")
    MODEL_ENDPOINT_NOT_JSON = (-10009, "모델 API ERROR (NOT JSON)")
    MODEL_ENDPOINT_CALL_ERROR = (-10010, "모델 API CALL ERROR")
    MODEL_ENDPOINT_RESP_ERROR = (-10011, "모델 API CALL RESP ERROR (NOT JSON)")

    # LLM Process
    LLM_CONTENT_IS_EMPTY = (-10101, "빈 값입니다.")
    LLM_CONTENT_PROCESS_STOPPED_IN_INTENT = (-10102, "LLM 처리 로직에 따라 작업을 중단하였습니다.")
    LLM_CONTENT_PROCESS_ERROR = (-10103, "LLM Content 처리 중 에러가 발생하였습니다.")
    LLM_CONTENT_PREPROCESS_ERROR = (-10111, "LLM Content 전처리 중 에러가 발생하였습니다.")
    LLM_CONTENT_PREPROCESS_FUNC_NOT_FOUND = (-10112, "LLM Content 전처리 함수를 찾을 수 없습니다.")
    LLM_CONTENT_PREPROCESS_FUNC_NOT_CALLABLE = (-10113, "LLM Content 전처리 함수가 잘못 선언되었습니다.")
    LLM_CONTENT_PREPROCESS_FUNC_ARGS_ERROR = (-10114, "LLM Content 전처리 함수 argument가 맞지 않습니다.")
    LLM_CONTENT_PREPROCESS_FUNC_ERROR = (-10115, "LLM Content 전처리 함수 동작 중 에러가 발생하였습니다.")
    LLM_CONTENT_POSTPROCESS_ERROR = (-10121, "LLM Content 후처리 중 에러가 발생하였습니다.")
    LLM_CONTENT_POSTPROCESS_FUNC_NOT_FOUND = (-10122, "LLM Content 후처리 함수를 찾을 수 없습니다.")
    LLM_CONTENT_POSTPROCESS_FUNC_NOT_CALLABLE = (-10123, "LLM Content 후처리 함수가 잘못 선언되었습니다.")
    LLM_CONTENT_POSTPROCESS_FUNC_ARGS_ERROR = (-10124, "LLM Content 후처리 함수 argument가 맞지 않습니다.")
    LLM_CONTENT_POSTPROCESS_FUNC_ERROR = (-10125, "LLM Content 후처리 함수 동작 중 에러가 발생하였습니다.")
    CONTENT_IS_EMPTY = (-10199, "빈 값입니다.")

    # Prompt
    PROMPT_NOT_SET = (-10201, "PROMPT가 설정되지 않았습니다.")
    PROMPT_NOT_FOUND = (-10202, "PROMPT를 찾을 수 없습니다.")
    PROMPT_FOR_COMPLETION_NOT_SET = (-10203, "PROMPT가 설정되지 않았습니다.: Completion")
    PROMPT_FOR_COMMENT_NOT_SET = (-10204, "PROMPT가 설정되지 않았습니다.: Comment")
    PROMPT_FOR_REFACTOR_NOT_SET = (-10205, "PROMPT가 설정되지 않았습니다.: Refactor")
    PROMPT_FOR_EXPLANATION_NOT_SET = (-10206, "PROMPT가 설정되지 않았습니다.: Explanation")
    PROMPT_FOR_TRANSLATION_NOT_SET = (-10207, "PROMPT가 설정되지 않았습니다.: Translation")
    PROMPT_FOR_ANSISQL_TRANSLATION_NOT_SET = (-10208, "PROMPT가 설정되지 않았습니다.: Translation(ANSI SQL)")
    PROMPT_FOR_SQL_NOT_SET = (-10209, "PROMPT가 설정되지 않았습니다.: SQL")
    PROMPT_FOR_SECURECODING_NOT_SET = (-10210, "PROMPT가 설정되지 않았습니다.: SecureCoding")
    PROMPT_FOR_TEST_GENERATION_NOT_SET = (-10211, "PROMPT가 설정되지 않았습니다.: TestGen")
    PROMPT_TYPE_NOT_SUPPORTED = (-10212, "해당 PROMPT 타입은 지원하지 않습니다.")

    # SERVICE
    AZURE_SERVICE_IS_NULL_OR_EMPTY = (-10301, "요청한 서비스가 유효하지 않습니다.")
    TOKEN_IS_TOO_LONG = (-10302, "토큰의 길이가 허용치를 초과했습니다.")
    TOKEN_OVERFLOW = (-10303, "가용 토큰을 모두 사용하였습니다. 관리자에게 문의하세요.")

    # EMBEDDING
    EMBEDDING_FILE_NOT_EXIST = (-10900, "파일을 찾을 수 없습니다.")
    EMBEDDING_VECTOR_NOT_EXIST = (-10901, "uploading 대상 Vector가 없습니다.")
    EMBEDDING_INDEX_NOT_EXIST = (-10902, "Index를 찾을 수 없습니다.")
    EMBEDDING_FILE_FORMAT_NOT_SUPPORTED = (-10903, "지원하지 않는 파일 포맷입니다.")

    # Custom Code
    CUSTOM_CODE_ERROR = (-10400, "사용자 코드 실행 오류가 발생하였습니다.")

    # FINETUNE
    FINETUNE_MODEL_NOT_FOUND = (-11000, "FineTune 모델을 찾을 수 없습니다.")
    FINETUNE_MODEL_ALREADY_EXISTS = (-11001, "FineTune 모델이 이미 존재합니다.")
    FINETUNE_REPO_NOT_EXISTS = (-11002, "FineTune Repository를 찾을 수 없습니다.")
    FINETUNE_DATA_PATH_NOT_EXISTS = (-11003, "Finetune에 사용할 dataset path 가 없습니다.")
    FINETUNE_DATA_PATH_FILE_NOT_EXISTS = (-11004, "Finetune에 사용할 dataset file이 없습니다..")

    def __init__(self, code: int, message: str):
        self.code = code
        code_msg: CodeMessage | None = code_messages.find_by_code(code)
        if code_msg and code_msg.message:
            self.message = code_msg.message
        else:
            self.message = message

        cls = self.__class__
        if any(self.value == e.value for e in cls):
            a = self.name
            e = cls(self.value, self.message).name
            raise ValueError("aliases not allowed to prevent duplicatation:  %r --> %r" % (a, e))

    @property
    def describe(self):
        # self is the member here
        return self.name, self.code, self.message

    # def __new__(cls, code: int, message: str):
    #     obj = object.__new__(cls)
    #     obj.code = code
    #     obj.message = message
    #     return obj
    # def __init__(cls, code: int, message: str):
    #     obj = object.__new__(cls)
    #     code_msg: Optional[CodeMessage] = code_messages.find_by_code(code)
    #     if code_msg is None:
    #         obj.message = message
    #     else:
    #         obj.message = code_msg.message

    #     if any(obj.value == e.value for e in cls):
    #         a = obj.name
    #         e = cls(obj.value, obj.message).name
    #         raise ValueError(
    #             "aliases not allowed to prevent duplicatation:  %r --> %r"
    #             % (a, e))

    def __str__(self) -> str:
        return f"[{self.code}]: {self.message}"

    @classmethod
    def of(cls, code: int) -> "ResponseCode":
        for item in cls:
            if item.value[0] == code:
                return item
        return super()._missing_(code)
