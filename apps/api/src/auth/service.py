import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.auth.config import get_auth_settings
from src.auth.constants import REFRESH_TOKEN_PREFIX
from src.auth.exceptions import RefreshError
from src.database import get_pool


def _now() -> datetime:
    return datetime.now(UTC)


def _new_token() -> str:
    return REFRESH_TOKEN_PREFIX + secrets.token_urlsafe(32)


def _hash(token: str) -> bytes:
    return hashlib.sha256(token.encode()).digest()


@dataclass
class Rotated:
    user_id: int
    family_id: UUID
    roles: list[str]
    refresh_token: str


async def create_family(conn, user_id: int, user_agent: str) -> tuple[UUID, str]:
    auth_settings = get_auth_settings()
    now = _now()
    absolute = now + timedelta(seconds=auth_settings.SESSION_ABSOLUTE_TTL)
    family_id = await conn.fetchval(
        """INSERT INTO auth_session_families
               (user_id, created_at, last_used_at, absolute_expires_at, user_agent)
           VALUES ($1, $2, $2, $3, $4) RETURNING id""",
        user_id,
        now,
        absolute,
        user_agent[:300],
    )
    token = _new_token()
    await conn.execute(
        """INSERT INTO auth_refresh_tokens (family_id, token_hash, issued_at, expires_at)
           VALUES ($1, $2, $3, $4)""",
        family_id,
        _hash(token),
        now,
        min(now + timedelta(seconds=auth_settings.REFRESH_IDLE_TTL), absolute),
    )
    return family_id, token


async def rotate(presented: str) -> Rotated:
    auth_settings = get_auth_settings()
    now = _now()
    grace = timedelta(seconds=auth_settings.REFRESH_REUSE_GRACE)
    outcome: Rotated | RefreshError

    async with get_pool().acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                """SELECT t.id, t.expires_at, t.used_at,
                          f.id AS family_id, f.user_id, f.revoked_at, f.absolute_expires_at,
                          u.status, u.roles
                   FROM auth_refresh_tokens t
                   JOIN auth_session_families f ON f.id = t.family_id
                   JOIN app_users u ON u.id = f.user_id
                   WHERE t.token_hash = $1
                   FOR UPDATE OF t, f""",
                _hash(presented),
            )

            if row is None:
                outcome = RefreshError("unknown")
            elif row["revoked_at"] is not None:
                outcome = RefreshError("revoked")
            elif now >= row["expires_at"] or now >= row["absolute_expires_at"]:
                outcome = RefreshError("expired")
            elif row["status"] != "active":
                outcome = RefreshError("inactive")
            elif row["used_at"] is not None and now - row["used_at"] > grace:
                await conn.execute(
                    """UPDATE auth_session_families
                       SET revoked_at = $2, revoke_reason = 'reuse_detected'
                       WHERE id = $1""",
                    row["family_id"],
                    now,
                )
                outcome = RefreshError("reuse_detected")
            else:
                if row["used_at"] is None:
                    await conn.execute(
                        "UPDATE auth_refresh_tokens SET used_at = $2 WHERE id = $1",
                        row["id"],
                        now,
                    )
                new_token = _new_token()
                await conn.execute(
                    """INSERT INTO auth_refresh_tokens
                           (family_id, parent_id, token_hash, issued_at, expires_at)
                       VALUES ($1, $2, $3, $4, $5)""",
                    row["family_id"],
                    row["id"],
                    _hash(new_token),
                    now,
                    min(
                        now + timedelta(seconds=auth_settings.REFRESH_IDLE_TTL),
                        row["absolute_expires_at"],
                    ),
                )
                await conn.execute(
                    "UPDATE auth_session_families SET last_used_at = $2 WHERE id = $1",
                    row["family_id"],
                    now,
                )
                outcome = Rotated(
                    row["user_id"], row["family_id"], list(row["roles"]), new_token
                )

    if isinstance(outcome, RefreshError):
        raise outcome
    return outcome


async def revoke_family_by_token(presented: str, reason: str) -> None:
    async with get_pool().acquire() as conn:
        await conn.execute(
            """UPDATE auth_session_families f
               SET revoked_at = now(), revoke_reason = $2
               FROM auth_refresh_tokens t
               WHERE t.family_id = f.id AND t.token_hash = $1 AND f.revoked_at IS NULL""",
            _hash(presented),
            reason,
        )


async def revoke_family(family_id: UUID, user_id: int, reason: str) -> bool:
    async with get_pool().acquire() as conn:
        result = await conn.execute(
            """UPDATE auth_session_families SET revoked_at = now(), revoke_reason = $3
               WHERE id = $1 AND user_id = $2 AND revoked_at IS NULL""",
            family_id,
            user_id,
            reason,
        )
    return result == "UPDATE 1"


async def revoke_all(user_id: int, reason: str) -> None:
    async with get_pool().acquire() as conn:
        await conn.execute(
            """UPDATE auth_session_families SET revoked_at = now(), revoke_reason = $2
               WHERE user_id = $1 AND revoked_at IS NULL""",
            user_id,
            reason,
        )


async def list_active(user_id: int) -> list[dict]:
    async with get_pool().acquire() as conn:
        rows = await conn.fetch(
            """SELECT id, created_at, last_used_at, user_agent
               FROM auth_session_families
               WHERE user_id = $1 AND revoked_at IS NULL AND absolute_expires_at > now()
               ORDER BY last_used_at DESC""",
            user_id,
        )
    return [dict(r) for r in rows]


async def cleanup_expired() -> None:
    async with get_pool().acquire() as conn:
        await conn.execute(
            "DELETE FROM auth_refresh_tokens WHERE expires_at < now() - interval '7 days'"
        )
        await conn.execute(
            """DELETE FROM auth_session_families
               WHERE (revoked_at IS NOT NULL AND revoked_at < now() - interval '90 days')
                  OR absolute_expires_at < now() - interval '90 days'"""
        )
