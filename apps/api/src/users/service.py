from src.database import get_pool
from src.users.schemas import User


def _to_user(row) -> User:
    return User(
        id=row["id"],
        email=row["email"],
        steam_id=row["steam_id"],
        status=row["status"],
        roles=list(row["roles"]),
    )


async def get_user(user_id: int) -> User | None:
    async with get_pool().acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT
                id,
                email,
                steam_id,
                status,
                roles
            FROM app_users
            WHERE id = $1
            """,
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
            id,
            email,
            steam_id,
            status,
            roles
        FROM app_users
        WHERE steam_id = $1
          AND email IS NOT NULL
          AND password_hash IS NOT NULL
        """,
        int(steamid),
    )

    return _to_user(row) if row else None

async def link_steam_account(
    conn,
    user_id: int,
    steamid: str,
) -> User | None:

    row = await conn.fetchrow(
        """
        UPDATE app_users
        SET steam_id = $1
        WHERE id = $2
          AND email IS NOT NULL
          AND password_hash IS NOT NULL
        RETURNING
            id,
            email,
            steam_id,
            status,
            roles
        """,
        int(steamid),
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
            steam_id,
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

    return _to_user(row)


async def get_user_with_password_by_email(
    conn,
    email: str,
) -> tuple[User, str | None] | None:

    row = await conn.fetchrow(
        """
        SELECT
            id,
            email,
            password_hash,
            steam_id,
            status,
            roles
        FROM app_users
        WHERE email = $1
        """,
        email,
    )

    if row is None:
        return None

    return _to_user(row), row["password_hash"]