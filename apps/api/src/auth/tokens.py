import time
import uuid

import jwt

from src.auth.config import get_auth_settings
from src.auth.constants import ACCESS_AUD, JWT_ALGORITHMS, STATE_AUD
from src.auth.exceptions import TokenError
from src.config import get_settings


def _issuer() -> str:
    return get_settings().BASE_URL


def _encode(claims: dict, ttl: int, aud: str) -> str:
    auth_settings = get_auth_settings()
    now = int(time.time())
    payload = {
        "iss": _issuer(),
        "aud": aud,
        "iat": now,
        "nbf": now,
        "exp": now + ttl,
        "jti": uuid.uuid4().hex,
        **claims,
    }
    return jwt.encode(
        payload,
        auth_settings.JWT_PRIVATE_KEY_PEM,
        algorithm="EdDSA",
        headers={"kid": auth_settings.JWT_ACTIVE_KID},
    )


def _decode(token: str, aud: str, expected_typ: str) -> dict:
    auth_settings = get_auth_settings()
    try:
        kid = jwt.get_unverified_header(token).get("kid")
        public_key = auth_settings.public_keys.get(kid)
        if public_key is None:
            raise TokenError("invalid")
        claims = jwt.decode(
            token,
            public_key,
            algorithms=JWT_ALGORITHMS,
            audience=aud,
            issuer=_issuer(),
            leeway=auth_settings.CLOCK_LEEWAY,
            options={"require": ["exp", "iat", "nbf", "iss", "aud", "typ"]},
        )
    except jwt.ExpiredSignatureError as e:
        raise TokenError("expired") from e
    except jwt.InvalidTokenError as e:
        raise TokenError("invalid") from e
    if claims.get("typ") != expected_typ:
        raise TokenError("invalid")
    return claims


def issue_access(user_id: int, family_id: str, roles: list[str]) -> str:
    return _encode(
        {"sub": str(user_id), "sid": str(family_id), "typ": "access", "roles": roles},
        get_auth_settings().ACCESS_TTL,
        ACCESS_AUD,
    )


def verify_access(token: str) -> dict:
    return _decode(token, ACCESS_AUD, "access")


def issue_openid_state(nonce: str, next_path: str) -> str:
    return _encode(
        {"typ": "oid_state", "nonce": nonce, "next": next_path},
        get_auth_settings().OPENID_STATE_TTL,
        STATE_AUD,
    )


def verify_openid_state(token: str) -> dict:
    return _decode(token, STATE_AUD, "oid_state")
