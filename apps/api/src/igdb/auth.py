import asyncio
import time

import httpx

from src.igdb.config import get_igdb_settings

TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"


class TwitchTokenManager:
    def __init__(self, client: httpx.AsyncClient):
        self._client = client
        self._token: str | None = None
        self._expires_at = 0.0
        self._lock = asyncio.Lock()

    def _is_fresh(self) -> bool:
        return self._token is not None and time.time() < self._expires_at - 300

    async def get(self, force_refresh: bool = False) -> str:
        if not force_refresh and self._is_fresh():
            return self._token
        async with self._lock:
            if not force_refresh and self._is_fresh():
                return self._token
            settings = get_igdb_settings()
            r = await self._client.post(
                TWITCH_TOKEN_URL,
                params={
                    "client_id": settings.TWITCH_CLIENT_ID,
                    "client_secret": settings.TWITCH_CLIENT_SECRET,
                    "grant_type": "client_credentials",
                },
            )
            r.raise_for_status()
            data = r.json()
            self._token = data["access_token"]
            self._expires_at = time.time() + data["expires_in"]
            return self._token
