import traceback
import uuid
from types import TracebackType

from fastapi.exceptions import HTTPException

from .response_code import ResponseCode

__all__ = [
    "AIRuntimeException",
    "HandledException",
    "UnHandledException",
    "AuthenticationException",
    "URLParseException",
    "JsonException",
    "FormatterException",
    "AsyncThreadPoolTaskException",
    "BackgroundTaskException",
    "NotFoundException",
]


def get_last_traceback(tb: TracebackType) -> TracebackType:
    new_tb = tb.tb_next
    if new_tb is None:
        return tb
    else:
        return get_last_traceback(new_tb)


class AIRuntimeException(HTTPException):
    errorCode = -1
    errorMessage = "실패"
    traceId = None
    systemMessage = None
    systemStackTrace = None


# Not set against GraphQLError for now


class HandledException(HTTPException):
    """Application-managed Exception, which is an exception wrapper.

    This Exception is designed to handle the exceptions raised from
    application API is responsing. When it is raised, it is catched by
    exception handlers and `ErrorResponse` is responsed.


    Parameters
    ----------
    resp_code: ResponseCode
        An application-managed error case. it has its own `code` and `msg` to logging.

    e: Exception
        An system raised exception to wrap.

    code: int (default: None)
        It needed if `resp_code` is not given.

    msg: str (default: None)
        It needed if `resp_code` is not given.


    Examples
    --------
    >>> import requests
    >>> from .types.exceptions import ResponseCode, HandledException
    >>> try:
    ...     r = requests.get("https://google.com")
    ... except Exception as e:
    ...     raise HandledException(ResponseCode.RESTCLIENT_REQUEST_ERROR, e=e)

    """

    # errorCode
    code: int
    # errorMessage
    message: str

    traceId: str
    systemMessage: str | None = None
    systemStackTrace: str | None = None

    def __init__(
        self,
        resp_code: ResponseCode,
        e: Exception | None = None,
        code: int | None = None,
        msg: str | None = None,
    ) -> None:
        super(HTTPException, self).__init__(status_code=500, detail=resp_code.message)
        self.code = resp_code.code
        self.message = resp_code.message

        delimeter = ": "
        if msg is not None:
            self.message = delimeter.join(
                [
                    self.message,
                    msg,
                ],
            )
        self.traceId = gen_logtrace_id()

        if e is None:
            self.systemMessage = self.message
            exc_type = type(self)
            filename = ""
            name = ""
            line = ""
            self.systemStackTrace = delimeter.join(
                [
                    f"{{ErrorType: {exc_type}}}",
                ],
            )
        else:
            tb = e.__traceback__
            last_tb = get_last_traceback(tb)
            exc_type = e.__class__.__name__
            filename = last_tb.tb_frame.f_code.co_filename
            name = last_tb.tb_frame.f_code.co_name
            line = last_tb.tb_lineno
            stack = "".join(traceback.format_tb(e.__traceback__))
            exc_msg = f"{exc_type}: {e!s}"
            self.systemMessage = f"{self.message}: {exc_msg}"
            self.systemStackTrace = "\n".join(
                [
                    f"ErrorType: {exc_type}",
                    f"File: {filename}",
                    f"Name: {name}",
                    f"Line: {line}",
                    f"Traceback: \n{stack}{exc_msg}",
                ],
            )

    @property
    def logMessage(self) -> str:
        return "\n" + "\n".join(
            [
                "=" * 50,
                f"TraceID: {self.traceId}",
                f"CODE: {self.code}",
                f"MSG: {self.message}",
                f"SYSMSG: {self.systemMessage}",
                "=" * 50,
                f"StackTrace: \n{self.systemStackTrace}",
            ],
        )


def gen_logtrace_id() -> str:
    return f"log-{uuid.uuid4()!s}"


class UnHandledException(HandledException):
    def __init__(self, e: Exception = None, code: int = None, msg: str = None):
        super().__init__(ResponseCode.UNDEFINED_ERROR, e=e, code=code, msg=msg)


class AuthenticationException(HandledException):
    def __init__(
        self,
        resp_code: ResponseCode,
        e: Exception | None = None,
        code: int | None = None,
        msg: str | None = None,
    ) -> None:
        super().__init__(resp_code, e=e, code=code, msg=msg)
        self.status_code = 401


class NotFoundException(HandledException):
    def __init__(
        self,
        resp_code: ResponseCode,
        e: Exception | None = None,
        code: int | None = None,
        msg: str | None = None,
    ) -> None:
        super().__init__(resp_code, e=e, code=code, msg=msg)
        self.status_code = 404


class URLParseException(HandledException): ...


class JsonException(HandledException): ...


class FormatterException(HandledException): ...


class CongigurationException(HandledException): ...


class AsyncThreadPoolTaskException(HandledException): ...


class DBConnectionException(HandledException): ...


class BackgroundTaskException(HandledException):
    """HandledException for BackgroundTasks.

    This Exception is designed to handle the exceptions raised from
    BackgroundTasks and prevent exception handlers from responsing
    the request already responsed.


    Parameters
    ----------
    resp_code: ResponseCode
        An application-managed error case. it has its own `code` and `msg` to logging.

    e: Exception
        An system raised exception to wrap.

    code: int (default: None)
        It needed if `resp_code` is not given.

    msg: str (default: None)
        It needed if `resp_code` is not given.


    Examples
    --------
    >>> import requests
    >>> from .types.exceptions import ResponseCode, BackgroundTaskException
    >>> try:
    ...     r = requests.get("https://google.com")
    ... except Exception as e:
    ...     raise BackgroundTaskException(ResponseCode.RESTCLIENT_REQUEST_ERROR, e=e)

    """
