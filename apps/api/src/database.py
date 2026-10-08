import asyncpg

from src.config import get_settings

_pool: asyncpg.Pool | None = None


async def connect(dsn: str | None = None) -> None:
    global _pool
    _pool = await asyncpg.create_pool(
        dsn or get_settings().DATABASE_URL, min_size=1, max_size=10
    )


async def disconnect() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("La base de datos no está inicializada")
    return _pool
