from typing import Dict, Optional
import functools
import inspect

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Header, Request
from typing_extensions import Annotated


from mainapp.core.types.enums.code import ClientType
from mainapp.core.types.exceptions import ResponseCode, HandledException


__all__ = [
    "get_client_ip",
    "extract_client_type",
]

# async def get_token_header(x_token: str = Header(...)):
#     if x_token != "fake-super-secret-token":
#         raise HTTPException(status_code=400, detail="X-Token header invalid")


# async def get_query_token(token: str):
#     if token != "jessica":
#         raise HTTPException(
#             status_code=400, detail="No Jessica token provided")


async def get_session(request: Request):
    # here I get sqlalchemy's scoped_session, which should be the same instance per thread
    request.state.session = request.app.state.database.get_session()
    try:
        yield request.state.session
    finally:
        request.state.session.close()


async def managed_transaction(func):

    @functools.wraps(func)
    async def wrap_func(*args, session: Session = Depends(get_session), **kwargs):
        try:
            if inspect.iscoroutinefunction(func):
                result = await func(*args, session=session, **kwargs)
            else:
                result = func(*args, session=session, **kwargs)
            session.commit()
        except HTTPException as e:
            session.rollback()
            raise e
        # don't close session here, or you won't be able to response
        return result

    return wrap_func



async def get_client_ip(
        x_real_ip: Annotated[str, Header()] = None,
        x_forwarded_for: Annotated[str, Header()] = None,
        ) -> Dict[str, str]:

    return {
        "x_real_ip": x_real_ip,
        "x_forwarded_for": x_forwarded_for,
    }

async def extract_client_type(client_type: Optional[ClientType] = Header(None)):
    match client_type:
        case None | ClientType.CUSTOM:
            return ClientType.CUSTOM
        case ClientType.VSCODE:
            return ClientType.VSCODE
        case ClientType.JETBRAINS:
            return ClientType.JETBRAINS
        case ClientType.ECLIPSE:
            return ClientType.ECLIPSE
        case _:
            raise HandledException(ResponseCode.INVALID_CLIENT_TYPE)
