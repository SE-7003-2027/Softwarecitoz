from typing import Annotated
from urllib.parse import urlparse

from fastapi import Depends, HTTPException, Request

from src.auth.constants import ACCESS_COOKIE
from src.auth.exceptions import TokenError
from src.auth.tokens import verify_access
from src.config import get_settings
from src.database import get_pool
from src.users import service as users_service
from src.users.schemas import User


def _allowed_origin() -> str:
    u = urlparse(get_settings().BASE_URL)
    return f"{u.scheme}://{u.netloc}"


def _extract_token(request: Request) -> str:
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:]
    return request.cookies.get(ACCESS_COOKIE, "")


async def current_claims(request: Request) -> dict:
    try:
        return verify_access(_extract_token(request))
    except TokenError as e:
        code = "token_expired" if str(e) == "expired" else "invalid_token"
        raise HTTPException(
            401, detail=code, headers={"WWW-Authenticate": f'Bearer error="{code}"'}
        ) from None


async def current_active_user(claims: dict = Depends(current_claims)) -> User:
    user_id = int(claims["sub"])
    async with get_pool().acquire() as conn:
        ok = await conn.fetchval(
            """SELECT 1 FROM app_users u
               JOIN auth_session_families f ON f.user_id = u.id
               WHERE u.id = $1 AND f.id = $2::uuid
                 AND u.status = 'active' AND f.revoked_at IS NULL""",
            user_id,
            claims["sid"],
        )
    user = await users_service.get_user(user_id) if ok else None
    if user is None:
        raise HTTPException(401, detail="invalid_token")
    return user


async def require_admin(user: User = Depends(current_active_user)) -> User:
    if "admin" not in user.roles:
        raise HTTPException(403)
    return user


async def require_same_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if origin is not None and origin != _allowed_origin():
        raise HTTPException(403, "Origen no permitido")


ClaimsDep = Annotated[dict, Depends(current_claims)]
ActiveUserDep = Annotated[User, Depends(current_active_user)]
AdminDep = Annotated[User, Depends(require_admin)]
