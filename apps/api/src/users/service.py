from src.database import get_pool
from src.users.schemas import User



def _to_user(row) -> User:
    return User(
        id=row["id"],
        status=row["status"],
        roles=list(row["roles"]),
        email=row["email"],
        steam_id=row["steam_id"],
    )

_USER_SELECT = """
SELECT
    u.id,
    u.status,
    u.roles,
    u.email,
    sp.steamid AS steam_id

FROM app_users AS u

LEFT JOIN players AS p
    ON p.auth_user_id = u.id

LEFT JOIN steam_profiles AS sp
    ON sp.player_id = p.id
"""


async def get_user(user_id: int) -> User | None:
    async with get_pool().acquire() as conn:

        row = await conn.fetchrow(
            _USER_SELECT + " WHERE u.id = $1",
            user_id,
        )

    return _to_user(row) if row else None



async def get_user_by_steam(
    conn,
    steamid: str,
) -> User | None:

    row = await conn.fetchrow(
        """
        SELECT
            u.id,
            u.email,
            sp.steamid AS steam_id,
            u.status,
            u.roles

        FROM steam_profiles AS sp

        JOIN players AS p
            ON p.id = sp.player_id

        JOIN app_users AS u
            ON u.id = p.auth_user_id

        WHERE sp.steamid = $1
          AND u.email IS NOT NULL
          AND u.password_hash IS NOT NULL
        """,
        int(steamid),
    )

    return _to_user(row) if row else None

async def link_steam_account(
    conn,
    user_id: int,
    steamid: str,
) -> User | None:

    steam_id = int(steamid)

    # Buscamos la cuenta de Chaos y su perfil.
    player = await conn.fetchrow(
        """
        SELECT
            u.id AS user_id,
            p.id AS player_id

        FROM app_users AS u

        JOIN players AS p
            ON p.auth_user_id = u.id

        WHERE u.id = $1
          AND u.email IS NOT NULL
          AND u.password_hash IS NOT NULL
        """,
        user_id,
    )

    if player is None:
        return None

    # Vinculamos Steam al perfil de Chaos.
    # steamid es UNIQUE, así que una misma cuenta
    # de Steam no puede pertenecer a dos jugadores.
    await conn.execute(
        """
        INSERT INTO steam_profiles (
            player_id,
            steamid,
            last_synced_at
        )
        VALUES (
            $1,
            $2,
            now()
        )

        ON CONFLICT (player_id)
        DO UPDATE SET
            steamid = EXCLUDED.steamid,
            last_synced_at = now()
        """,
        player["player_id"],
        steam_id,
    )

    row = await conn.fetchrow(
        _USER_SELECT + " WHERE u.id = $1",
        user_id,
    )

    return _to_user(row) if row else None

async def create_user_with_email(
    conn,
    email: str,
    password_hash: str,
) -> User:

    row = await conn.fetchrow(
        """
        INSERT INTO app_users (
            email,
            password_hash
        )
        VALUES ($1, $2)
        RETURNING
            id,
            email,
            status,
            roles
        """,
        email,
        password_hash,
    )

    await conn.execute(
        """
        INSERT INTO players (auth_user_id)
        VALUES ($1)
        ON CONFLICT (auth_user_id)
        DO NOTHING
        """,
        row["id"],
    )

    return User(
        id=row["id"],
        status=row["status"],
        roles=list(row["roles"]),
        email=row["email"],
        steam_id=None,
    )


async def get_user_with_password_by_email(
    conn,
    email: str,
) -> tuple[User, str | None] | None:

    row = await conn.fetchrow(
        """
        SELECT
            u.id,
            u.email,
            u.password_hash,
            sp.steamid AS steam_id,
            u.status,
            u.roles

        FROM app_users AS u

        LEFT JOIN players AS p
            ON p.auth_user_id = u.id

        LEFT JOIN steam_profiles AS sp
            ON sp.player_id = p.id

        WHERE u.email = $1
        """,
        email,
    )

    if row is None:
        return None

    return _to_user(row), row["password_hash"]