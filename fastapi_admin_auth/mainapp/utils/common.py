
import calendar
import datetime
from collections.abc import Callable

import jwt
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils import timezone

__all__ = [
    "make_jwt_token",
    "build_azure_header",
    "build_basic_header",
    "is_installed_app"
]


def build_azure_header(token: str) -> None:
    """header 값 설정
    Args:
        token(jwt_token, api_key 등)
    Returns:
    """
    return {
        "api-key": token
    }
    

def build_basic_header() -> None:
    return {
        "Content-Type": "application/json"
    }


def make_jwt_token(user):
    now = datetime.datetime.utcnow()
    token = jwt.encode({
        "client_id": user.id,
        "user_name": user.get_full_name(),
        "created_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expires_in": 60,
        "exp": calendar.timegm(now.utctimetuple()) + 3600,
    },
        'secret',
        algorithm="HS256")
    return token


def is_installed_app(app_name):
    return app_name in settings.INSTALLED_APPS

async def sync_to_async_wrapper(func: Callable, *args, **kwargs):
    async_func = sync_to_async(func, thread_sensitive=True)
    return await async_func(*args, **kwargs)