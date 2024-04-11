from typing import Union, Optional
import json

from functools import partial

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import FastAPIError, HTTPException, WebSocketRequestValidationError
from fastapi.exceptions import RequestValidationError as HTTPRequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from autologging import traced, logged
from corusapi.types.response import ErrorResponse
from corusapi.types.exceptions import (
    AIRuntimeException,
    HandledException,
    UnHandledException,
    AuthenticationException,
    URLParseException,
    JsonException,
    FormatterException,
    HarborClientException,
    CephClientException,
    S3ClientException,
    RestClientException,
    TektonClientException,
    KubernetesActionException,
    AttributeConverterException,
    AsyncThreadPoolTaskException,
    BackgroundTaskException,
)

# from kubernetes.config.config_exception import ConfigException


async def _handled_exception_handler(
        request: Request,
        e: Union[HandledException, UnHandledException]
) -> JSONResponse:
    return JSONResponse(
        status_code=e.status_code,
        content=jsonable_encoder(
            ErrorResponse(e=e)
        )
    )


async def _undefined_exception_handler(
        request: Request,
        e: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            ErrorResponse(e=e)
        )
    )

json_dumps = partial(json.dumps, indent=4, sort_keys=True, ensure_ascii=False)

def get_request_info(request: Request, body: Optional[bytes] = None) -> str:
    body_msg: str = ''
    try:
        if not body or body is None:
            body_msg = json_dumps(body)
        elif isinstance(body, bytes):
            try:
                body_msg = json_dumps(json.loads(body.decode()) or None)
            except json.JSONDecodeError:
                body_msg = str(body)
        elif isinstance(body, dict):
            body_msg = json_dumps(body)
        else:
            body_msg = str(body)
    except Exception:
        body_msg = str(body)

    return "\n".join([
        "=" * 50,
        "<Request>",
        f"client: {request.client}",
        f"method: {request.method}",
        f"url: {request.url}",
        f"headers: \n{json_dumps(dict(request.headers))}",
        f"body: \n{body_msg}",
        "=" * 50,
    ])


@logged
def set_global_exception_handlers(app: FastAPI) -> FastAPI:

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request, exc):
        managed_exc = UnHandledException(e=exc)
        set_global_exception_handlers._log.info(
            f"exception [{exc.__class__.__name__}], request is: \n{get_request_info(request)}" +
            f"\n{managed_exc.logMessage}"
        )
        return await _handled_exception_handler(request, managed_exc)

    @app.exception_handler(HTTPRequestValidationError)
    async def http_request_validation_exception_handler(request, exc):
        managed_exc = UnHandledException(e=exc)
        set_global_exception_handlers._log.info(
            f"exception [{exc.__class__.__name__}], request is: \n{get_request_info(request)}" +
            f"\n{managed_exc.logMessage}"
        )
        return await _handled_exception_handler(request, managed_exc)
    
    @app.exception_handler(WebSocketRequestValidationError)
    async def websocket_request_validation_exception_handler(request, exc):
        managed_exc = UnHandledException(e=exc)
        set_global_exception_handlers._log.error(
            f"exception [{exc.__class__.__name__}], request is: \n{get_request_info(request)}"
            f"\n{managed_exc.logMessage}"
        )
        return await request_validation_exception_handler(request, exc)

    @app.exception_handler(HandledException)
    async def handeled_exception_handler(request, exc):
        set_global_exception_handlers._log.error(
            f"exception [{exc.__class__.__name__}], request is: \n{get_request_info(request)}" +
            f"\n{exc.logMessage}")
        return await _handled_exception_handler(request, exc)

    @app.exception_handler(Exception)
    async def undefined_exception_handler(request, exc):
        managed_exc = UnHandledException(e=exc)
        set_global_exception_handlers._log.error(
            f"exception [{exc.__class__.__name__}], request is: \n{get_request_info(request)}" +
            f"\n{managed_exc.logMessage}")
        return await _handled_exception_handler(request, managed_exc)

    @app.exception_handler(BackgroundTaskException)
    async def background_task_exception_handler(request, exc):
         set_global_exception_handlers._log.error(
            f"exception [{exc.__class__.__name__}], request is: \n{get_request_info(request)}" +
            f"\n{exc.logMessage}")

    return app
