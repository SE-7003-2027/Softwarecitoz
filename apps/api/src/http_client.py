import httpx

_client: httpx.AsyncClient | None = None


async def start() -> None:
    global _client
    _client = httpx.AsyncClient(
        timeout=10.0,
        headers={
            "User-Agent": "SteamInsights/0.1 (+https://github.com/SE-7003-2027/proyecto-steam)"
        },
    )


async def stop() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def get_http_client() -> httpx.AsyncClient:
    if _client is None:
        raise RuntimeError("El cliente HTTP no está inicializado")
    return _client
