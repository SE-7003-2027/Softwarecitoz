import base64
import secrets
from uuid import UUID

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_public_key,
)
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

from src.audit.service import audit_log
from src.auth import service as auth_service
from src.auth.config import get_auth_settings
from src.auth.constants import CALLBACK_PATH, REFRESH_COOKIE, STATE_COOKIE
from src.auth.cookies import clear_auth_cookies, set_auth_cookies
from src.auth.dependencies import ActiveUserDep, require_same_origin
from src.auth.exceptions import OpenIDError, RefreshError, TokenError
from src.auth.openid import build_login_url, verify_callback
from src.auth.schemas import SessionOut
from src.auth.tokens import issue_access, issue_openid_state, verify_openid_state
from src.config import get_settings
from src.database import get_pool
from src.http_client import get_http_client
from src.ingestion.service import enqueue_express_ingest
from src.users import service as users_service

router = APIRouter(prefix="/auth", tags=["auth"])
jwks_router = APIRouter(tags=["auth"])


def _safe_next(path: str | None) -> str:
    if not path or not path.startswith("/") or path.startswith("//"):
        return "/"
    return path


def _clear_state_cookie(resp: RedirectResponse) -> None:
    resp.delete_cookie(
        STATE_COOKIE, path="/", secure=get_settings().COOKIE_SECURE, httponly=True
    )


@router.get("/steam/login")
async def steam_login(next: str | None = None):
    settings = get_settings()
    nonce = secrets.token_urlsafe(32)
    return_to = f"{settings.BASE_URL}{CALLBACK_PATH}?state={nonce}"
    resp = RedirectResponse(build_login_url(return_to, settings.BASE_URL), status_code=302)
    resp.set_cookie(
        STATE_COOKIE,
        issue_openid_state(nonce, _safe_next(next)),
        max_age=get_auth_settings().OPENID_STATE_TTL,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    return resp


@router.get("/steam/callback")
async def steam_callback(request: Request):
    settings = get_settings()
    params = dict(request.query_params)
    url_state = params.get("state", "")

    try:
        state = verify_openid_state(request.cookies.get(STATE_COOKIE, ""))
    except TokenError:
        raise HTTPException(400, "Login expirado o inválido") from None
    if not url_state or not secrets.compare_digest(url_state, state["nonce"]):
        raise HTTPException(400, "Estado de login inválido")

    if params.get("openid.mode") == "cancel":
        resp = RedirectResponse("/login?cancelled=1", status_code=303)
        _clear_state_cookie(resp)
        return resp

    expected_return_to = f"{settings.BASE_URL}{CALLBACK_PATH}?state={url_state}"
    try:
        steamid = await verify_callback(params, expected_return_to, get_http_client())
    except OpenIDError:
        raise HTTPException(401, "No se pudo verificar el inicio de sesión") from None

    async with get_pool().acquire() as conn:
        async with conn.transaction():
            user = await users_service.upsert_user_from_steam(conn, steamid)
            if user.status != "active":
                raise HTTPException(403, "Cuenta no disponible")
            family_id, refresh = await auth_service.create_family(
                conn, user.id, request.headers.get("user-agent", "")
            )

    await audit_log("login", user_id=user.id, family_id=family_id)
    await enqueue_express_ingest(steamid)

    resp = RedirectResponse(state["next"], status_code=303)
    _clear_state_cookie(resp)
    set_auth_cookies(resp, issue_access(user.id, family_id, user.roles), refresh)
    return resp


@router.post("/refresh", dependencies=[Depends(require_same_origin)])
async def refresh(request: Request):
    presented = request.cookies.get(REFRESH_COOKIE, "")
    try:
        r = await auth_service.rotate(presented)
    except RefreshError as e:
        if e.reason == "reuse_detected":
            await audit_log(
                "refresh_reuse_detected", detail=request.headers.get("user-agent")
            )
        resp = JSONResponse({"error": "reauth_required"}, status_code=401)
        clear_auth_cookies(resp)
        return resp

    resp = JSONResponse({"ok": True})
    set_auth_cookies(resp, issue_access(r.user_id, r.family_id, r.roles), r.refresh_token)
    return resp


@router.post("/logout", dependencies=[Depends(require_same_origin)])
async def logout(request: Request):
    presented = request.cookies.get(REFRESH_COOKIE)
    if presented:
        await auth_service.revoke_family_by_token(presented, "logout")
    resp = JSONResponse({"ok": True})
    clear_auth_cookies(resp)
    return resp


@router.post("/logout-all", dependencies=[Depends(require_same_origin)])
async def logout_all(user: ActiveUserDep):
    await auth_service.revoke_all(user.id, "logout_all")
    await audit_log("logout_all", user_id=user.id)
    resp = JSONResponse({"ok": True})
    clear_auth_cookies(resp)
    return resp


@router.get("/sessions", response_model=list[SessionOut])
async def sessions(user: ActiveUserDep):
    return await auth_service.list_active(user.id)


@router.delete("/sessions/{family_id}", dependencies=[Depends(require_same_origin)])
async def revoke_session(family_id: UUID, user: ActiveUserDep):
    if not await auth_service.revoke_family(family_id, user.id, "user_revoked"):
        raise HTTPException(404)
    await audit_log("session_revoked", user_id=user.id, family_id=family_id)
    return {"ok": True}


@jwks_router.get("/.well-known/jwks.json")
def jwks():
    keys = []
    for kid, pem in get_auth_settings().public_keys.items():
        raw = load_pem_public_key(pem.encode()).public_bytes(Encoding.Raw, PublicFormat.Raw)
        keys.append(
            {
                "kty": "OKP",
                "crv": "Ed25519",
                "use": "sig",
                "alg": "EdDSA",
                "kid": kid,
                "x": base64.urlsafe_b64encode(raw).rstrip(b"=").decode(),
            }
        )
    return {"keys": keys}
