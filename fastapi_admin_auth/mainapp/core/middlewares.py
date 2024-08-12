

from autologging import logged


from starlette.requests import Request
from starlette.types import Message, Receive, Scope, Send
from starlette.websockets import WebSocket

from starlette.middleware.exceptions import ExceptionMiddleware

from mainapp.core.types.exceptions import ResponseCode, HandledException, BackgroundTaskException
from mainapp.core.global_exception_handlers import get_request_info


__all__ = [
    "HandledExceptionMiddleware",
]


@logged
class HandledExceptionMiddleware(ExceptionMiddleware):

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        response_started = False

        async def sender(message: Message) -> None:
            nonlocal response_started

            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, sender)
        except Exception as exc:
            # This handles the exceptions from background_tasks which is already responsed.
            # Case message is "RuntimeError: Caught handled exception, but response already started."
            if scope["type"] == "http":
                request = Request(scope, receive=receive)
                request_msg = get_request_info(request)
                real_exc = exc.__cause__

                # Expected: raised from original ExceptionMiddleware
                if real_exc:
                    if isinstance(real_exc, HandledException):
                        self.__log.error(f"{real_exc.logMessage}\n{request_msg}")
                    else:
                        wrapped_exc = HandledException(ResponseCode.UNDEFINED_ERROR, e=real_exc)
                        self.__log.error(f"{wrapped_exc.logMessage}\n{request_msg}")
                else:
                    # Unexpected: Not raised from original ExceptionMiddleware
                    wrapped_exc = HandledException(ResponseCode.UNDEFINED_ERROR, e=exc)
                    self.__log.error(f"{wrapped_exc.logMessage}\n{request_msg}")

            elif scope["type"] == "websocket":
                websocket = WebSocket(scope, receive=receive, send=send)



@logged
class BackgroundTaskExceptionMiddleware(ExceptionMiddleware):

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        response_started = False

        async def sender(message: Message) -> None:
            nonlocal response_started

            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, sender)
        except Exception as exc:
            # This handles the exceptions from background_tasks which is already responsed.
            # Case message is "RuntimeError: Caught handled exception, but response already started."
            request = Request(scope)
            request_msg = get_request_info(request)
            real_exc = exc.__cause__
            # Expected: raised from original ExceptionMiddleware
            if real_exc:
                if isinstance(real_exc, BackgroundTaskException):
                    self.__log.error(f"{request_msg}\n{real_exc.logMessage}")
                else:
                    wrapped_exc = BackgroundTaskException(ResponseCode.UNDEFINED_ERROR, e=real_exc)
                    self.__log.error(f"{request_msg}\n{wrapped_exc.logMessage}")
            else:
                # Unexpected: Not raised from original ExceptionMiddleware
                wrapped_exc = BackgroundTaskException(ResponseCode.UNDEFINED_ERROR, e=exc)
                self.__log.error(f"{request_msg}\n{wrapped_exc.logMessage}")
