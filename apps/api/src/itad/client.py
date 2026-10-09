import httpx

from src.itad.config import get_itad_settings

ITAD_BASE_URL = "https://api.isthereanydeal.com"


async def itad_request(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    params: dict | None = None,
    json: object | None = None,
) -> object:
    r = await client.request(
        method,
        f"{ITAD_BASE_URL}{path}",
        params=params,
        json=json,
        headers={"ITAD-API-Key": get_itad_settings().ITAD_API_KEY},
    )
    r.raise_for_status()
    return r.json()
