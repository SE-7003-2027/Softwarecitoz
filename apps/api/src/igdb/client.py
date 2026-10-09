import httpx

from src.igdb.auth import TwitchTokenManager
from src.igdb.config import get_igdb_settings

IGDB_BASE_URL = "https://api.igdb.com/v4"


async def igdb_post(
    tm: TwitchTokenManager, client: httpx.AsyncClient, endpoint: str, query: str
) -> list[dict]:
    for attempt in range(2):
        token = await tm.get(force_refresh=attempt == 1)
        r = await client.post(
            f"{IGDB_BASE_URL}/{endpoint}",
            content=query,
            headers={
                "Client-ID": get_igdb_settings().TWITCH_CLIENT_ID,
                "Authorization": f"Bearer {token}",
            },
        )
        if r.status_code == 401 and attempt == 0:
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError("IGDB rechazó el token renovado")
