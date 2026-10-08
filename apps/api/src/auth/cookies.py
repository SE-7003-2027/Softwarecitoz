from fastapi import Response

from src.auth.config import get_auth_settings
from src.auth.constants import ACCESS_COOKIE, REFRESH_COOKIE, REFRESH_PATH
from src.config import get_settings


def set_auth_cookies(resp: Response, access: str, refresh: str) -> None:
    secure = get_settings().COOKIE_SECURE
    auth_settings = get_auth_settings()
    resp.set_cookie(
        ACCESS_COOKIE,
        access,
        max_age=auth_settings.ACCESS_TTL,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
    )
    resp.set_cookie(
        REFRESH_COOKIE,
        refresh,
        max_age=auth_settings.REFRESH_IDLE_TTL,
        httponly=True,
        secure=secure,
        samesite="strict",
        path=REFRESH_PATH,
    )


def clear_auth_cookies(resp: Response) -> None:
    secure = get_settings().COOKIE_SECURE
    resp.delete_cookie(ACCESS_COOKIE, path="/", secure=secure, httponly=True)
    resp.delete_cookie(REFRESH_COOKIE, path=REFRESH_PATH, secure=secure, httponly=True)
