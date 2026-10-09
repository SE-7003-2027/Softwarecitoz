import asyncio
import hashlib
import os
from pathlib import Path

import httpx
import pytest
from alembic import command
from alembic.config import Config
from fastapi import HTTPException

from src import database
from src.auth.constants import ACCESS_COOKIE, REFRESH_COOKIE
from src.auth.dependencies import current_active_user
from src.auth.exceptions import RefreshError
from src.auth.service import (
    create_family,
    revoke_all,
    revoke_family,
    revoke_family_by_token,
    rotate,
)
from src.auth.tokens import issue_access, verify_access
from src.config import get_settings
from src.users.service import upsert_user_from_steam

ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"
STEAMID_A = "76561198000000001"
STEAMID_B = "76561198000000002"


@pytest.fixture(scope="session")
def pg_url():
    try:
        from testcontainers.community.postgres import PostgresContainer

        container = PostgresContainer("postgres:16", driver=None)
        container.start()
    except Exception as e:
        pytest.skip(f"Docker no disponible: {e}")
    url = container.get_connection_url()
    previous = os.environ["DATABASE_URL"]
    os.environ["DATABASE_URL"] = url
    get_settings.cache_clear()
    command.upgrade(Config(str(ALEMBIC_INI)), "head")
    yield url
    os.environ["DATABASE_URL"] = previous
    get_settings.cache_clear()
    container.stop()


@pytest.fixture
async def pool(pg_url):
    await database.connect(pg_url)
    async with database.get_pool().acquire() as conn:
        await conn.execute("TRUNCATE app_users RESTART IDENTITY CASCADE")
    yield database.get_pool()
    await database.disconnect()


async def login(pool, steamid: str = STEAMID_A):
    async with pool.acquire() as conn:
        async with conn.transaction():
            user = await upsert_user_from_steam(conn, steamid)
            family_id, token = await create_family(conn, user.id, "pytest")
    return user, family_id, token


async def family_row(pool, family_id):
    return await pool.fetchrow(
        "SELECT revoked_at, revoke_reason FROM auth_session_families WHERE id = $1",
        family_id,
    )


async def test_upsert_is_idempotent(pool):
    user1, _, _ = await login(pool)
    user2, _, _ = await login(pool)
    assert user1.id == user2.id
    assert user1.roles == ["user"]
    assert user1.status == "active"


async def test_normal_rotation(pool):
    user, family_id, token = await login(pool)
    r = await rotate(token)
    assert r.user_id == user.id
    assert r.family_id == family_id
    assert r.refresh_token != token
    assert r.refresh_token.startswith("rt_")
    used_at = await pool.fetchval(
        "SELECT used_at FROM auth_refresh_tokens WHERE token_hash = $1",
        hashlib.sha256(token.encode()).digest(),
    )
    assert used_at is not None
    assert (await rotate(r.refresh_token)).family_id == family_id


async def test_unknown_token(pool):
    with pytest.raises(RefreshError) as e:
        await rotate("rt_no_existe")
    assert e.value.reason == "unknown"


async def test_reuse_after_grace_revokes_family(pool):
    _, family_id, token = await login(pool)
    latest = (await rotate(token)).refresh_token
    await pool.execute(
        "UPDATE auth_refresh_tokens SET used_at = used_at - interval '30 seconds' WHERE used_at IS NOT NULL"
    )

    with pytest.raises(RefreshError) as e:
        await rotate(token)
    assert e.value.reason == "reuse_detected"

    row = await family_row(pool, family_id)
    assert row["revoked_at"] is not None
    assert row["revoke_reason"] == "reuse_detected"

    with pytest.raises(RefreshError) as e:
        await rotate(latest)
    assert e.value.reason == "revoked"


async def test_concurrent_rotation_within_grace(pool):
    _, family_id, token = await login(pool)
    r1, r2 = await asyncio.gather(rotate(token), rotate(token))
    assert r1.refresh_token != r2.refresh_token
    used = await pool.fetchval(
        "SELECT count(*) FROM auth_refresh_tokens WHERE family_id = $1 AND used_at IS NOT NULL",
        family_id,
    )
    assert used == 1
    assert (await family_row(pool, family_id))["revoked_at"] is None


async def test_idle_expiry(pool):
    _, _, token = await login(pool)
    await pool.execute("UPDATE auth_refresh_tokens SET expires_at = now() - interval '1 second'")
    with pytest.raises(RefreshError) as e:
        await rotate(token)
    assert e.value.reason == "expired"


async def test_absolute_expiry(pool):
    _, _, token = await login(pool)
    await pool.execute(
        "UPDATE auth_session_families SET absolute_expires_at = now() - interval '1 second'"
    )
    with pytest.raises(RefreshError) as e:
        await rotate(token)
    assert e.value.reason == "expired"


async def test_rotated_token_never_outlives_session(pool):
    _, family_id, token = await login(pool)
    await pool.execute(
        "UPDATE auth_session_families SET absolute_expires_at = now() + interval '1 hour'"
    )
    r = await rotate(token)
    expires_at, absolute = await pool.fetchrow(
        """SELECT t.expires_at, f.absolute_expires_at
           FROM auth_refresh_tokens t JOIN auth_session_families f ON f.id = t.family_id
           WHERE t.token_hash = $1""",
        hashlib.sha256(r.refresh_token.encode()).digest(),
    )
    assert expires_at == absolute


async def test_banned_user(pool):
    user, family_id, token = await login(pool)
    claims = verify_access(issue_access(user.id, family_id, user.roles))
    assert (await current_active_user(claims)).id == user.id

    await pool.execute("UPDATE app_users SET status = 'banned' WHERE id = $1", user.id)

    with pytest.raises(RefreshError) as e:
        await rotate(token)
    assert e.value.reason == "inactive"
    with pytest.raises(HTTPException) as e:
        await current_active_user(claims)
    assert e.value.status_code == 401


async def test_logout_revokes_only_that_family(pool):
    _, family_1, token_1 = await login(pool)
    _, family_2, token_2 = await login(pool)
    await revoke_family_by_token(token_1, "logout")

    with pytest.raises(RefreshError) as e:
        await rotate(token_1)
    assert e.value.reason == "revoked"
    assert (await rotate(token_2)).family_id == family_2
    assert (await family_row(pool, family_1))["revoke_reason"] == "logout"


async def test_logout_all_blocks_sensitive_routes_immediately(pool):
    user, family_1, token_1 = await login(pool)
    _, _, token_2 = await login(pool)
    claims = verify_access(issue_access(user.id, family_1, user.roles))

    await revoke_all(user.id, "logout_all")

    for token in (token_1, token_2):
        with pytest.raises(RefreshError):
            await rotate(token)
    with pytest.raises(HTTPException) as e:
        await current_active_user(claims)
    assert e.value.status_code == 401


async def test_revoke_family_of_another_user(pool):
    user_a, _, _ = await login(pool, STEAMID_A)
    _, family_b, token_b = await login(pool, STEAMID_B)
    assert await revoke_family(family_b, user_a.id, "user_revoked") is False
    assert (await family_row(pool, family_b))["revoked_at"] is None
    assert (await rotate(token_b)).family_id == family_b


async def test_db_only_stores_hashes(pool):
    _, _, token = await login(pool)
    rotated = (await rotate(token)).refresh_token
    hashes = {bytes(r["token_hash"]) for r in await pool.fetch("SELECT token_hash FROM auth_refresh_tokens")}
    for t in (token, rotated):
        assert t.encode() not in hashes
        assert hashlib.sha256(t.encode()).digest() in hashes


@pytest.fixture
async def api(pool):
    from src.main import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="https://tuapp.com") as client:
        yield client


async def test_refresh_endpoint_sets_new_cookies(api, pool):
    _, _, token = await login(pool)
    r = await api.post("/auth/refresh", headers={"Cookie": f"{REFRESH_COOKIE}={token}"})
    assert r.status_code == 200
    assert ACCESS_COOKIE in r.cookies
    assert REFRESH_COOKIE in r.cookies

    again = await api.post(
        "/auth/refresh", headers={"Cookie": f"{REFRESH_COOKIE}=rt_no_existe"}
    )
    assert again.status_code == 401
    assert again.json() == {"error": "reauth_required"}


async def test_refresh_rejects_foreign_origin(api, pool):
    _, _, token = await login(pool)
    r = await api.post(
        "/auth/refresh",
        headers={"Cookie": f"{REFRESH_COOKIE}={token}", "Origin": "https://evil.example"},
    )
    assert r.status_code == 403


async def test_sessions_endpoints(api, pool):
    user_a, family_a, _ = await login(pool, STEAMID_A)
    _, family_b, _ = await login(pool, STEAMID_B)
    access = issue_access(user_a.id, family_a, user_a.roles)
    headers = {"Authorization": f"Bearer {access}"}

    listed = await api.get("/auth/sessions", headers=headers)
    assert listed.status_code == 200
    assert [s["id"] for s in listed.json()] == [str(family_a)]

    foreign = await api.delete(f"/auth/sessions/{family_b}", headers=headers)
    assert foreign.status_code == 404
    assert (await family_row(pool, family_b))["revoked_at"] is None

    own = await api.delete(f"/auth/sessions/{family_a}", headers=headers)
    assert own.status_code == 200
    assert (await api.get("/auth/sessions", headers=headers)).status_code == 401


async def test_protected_route_without_token(api):
    r = await api.get("/auth/sessions")
    assert r.status_code == 401
    assert r.json()["detail"] == "invalid_token"
    assert "WWW-Authenticate" in r.headers
