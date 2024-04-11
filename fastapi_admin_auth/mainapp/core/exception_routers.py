import datetime as dt
from collections.abc import Callable

from autologging import logged
from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

from corusapi.core.global_exception_handlers import _handled_exception_handler, get_request_info
from corusapi.types.exceptions import AuthenticationException, HandledException, ResponseCode
from corusapi.utils.uuid_gen import gen_transaction_id

# from corusapi.core.global_exception_handlers import get_request_info


__all__ = [
    "HandledExceptionLoggingRoute",
]


@logged
class HandledExceptionLoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def logging_route_handler(request: Request) -> Response:
            start_dt = dt.datetime.now()
            request_id = gen_transaction_id()
            try:
                response: Response = await original_route_handler(request)
                route_name = request.scope["route"].name
                duration = dt.datetime.now() - start_dt
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Request-Time"] = str(start_dt)
                response.headers["X-Response-Duration"] = str(duration.total_seconds())
                return response

            except Exception as exc:
                if request.headers.get("Content-Type"):
                    body = await request.body() if request.headers["Content-Type"] == "application/json" else b""
                else:
                    body = await request.body()

                request_msg = get_request_info(request, body=body)
                real_exc = exc.__cause__ or exc

                # Expected: raised from original ExceptionMiddleware
                if real_exc:
                    if isinstance(real_exc, AuthenticationException | HandledException):
                        self.__log.error(f"{real_exc.logMessage}\n{request_msg}")
                    elif isinstance(real_exc, RequestValidationError):
                        wrapped_exc = HandledException(ResponseCode.INVALID_VALUE_IN_REQUEST, e=real_exc)
                        self.__log.error(f"{wrapped_exc.logMessage}\n{request_msg}")
                        real_exc = wrapped_exc
                    else:
                        wrapped_exc = HandledException(ResponseCode.UNDEFINED_ERROR, e=real_exc)
                        self.__log.error(f"{wrapped_exc.logMessage}\n{request_msg}")
                        real_exc = wrapped_exc
                else:
                    # Unexpected: Not raised from original ExceptionMiddleware
                    wrapped_exc = HandledException(ResponseCode.UNDEFINED_ERROR, e=exc)
                    self.__log.error(f"{wrapped_exc.logMessage}\n{request_msg}")
                    real_exc = wrapped_exc

                # detail = {"errors": exc.errors(), "body": body.decode()}
                # raise HTTPException(status_code=422, detail=detail)
                return await _handled_exception_handler(request, e=real_exc)

        return logging_route_handler
