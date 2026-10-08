from src.database import get_pool
from src.users.schemas import User


def _to_user(row) -> User:
    return User(id=row["id"], status=row["status"], roles=list(row["roles"]))


async def get_user(user_id: int) -> User | None:
    async with get_pool().acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, status, roles FROM app_users WHERE id = $1", user_id
        )
    return _to_user(row) if row else None


async def upsert_user_from_steam(conn, steamid: str) -> User:
    row = await conn.fetchrow(
        """INSERT INTO app_users (steam_id) VALUES ($1)
           ON CONFLICT (steam_id) DO UPDATE SET steam_id = EXCLUDED.steam_id
           RETURNING id, status, roles""",
        int(steamid),
    )
    return _to_user(row)
