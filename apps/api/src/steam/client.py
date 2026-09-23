import httpx
from pydantic import SecretStr

from src.steam.exceptions import (
    SteamAuthError,
    SteamRateLimitedError,
    SteamUnavailableError,
)
from src.steam.schemas import (
    OwnedGamesRaw,
    PlayerSummariesRaw,
    PlayerSummaryRaw,
    RecentlyPlayedGamesRaw,
    SteamEnvelope,
)

ICON_URL = (
    "https://media.steampowered.com/steamcommunity/public/images/apps"
    "/{appid}/{icon_hash}.jpg"
)


class SteamClient:
    """
    Cliente de la Steam Web API.
    """

    def __init__(self, http: httpx.AsyncClient, api_key: SecretStr):
        self._http = http
        self._api_key = api_key

    async def _get(self, path: str, params: dict) -> dict:
        """
        Hace un GET a Steam y traduce los errores de httpx a errores
        de dominio. i.e. los que definimos
        """
        query = {
            "key": self._api_key.get_secret_value(),
            "format": "json",
            **params,
        }
        try:
            response = await self._http.get(path, params=query)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status in (401, 403):
                raise SteamAuthError() from None
            if status == 429:
                raise SteamRateLimitedError() from None
            raise SteamUnavailableError() from None
        except httpx.RequestError:
            raise SteamUnavailableError() from None
        return response.json()

    async def get_player_summary(self, steam_id: str) -> PlayerSummaryRaw | None:
        """
        Consulta ISteamUser/GetPlayerSummaries.

        Args:
            steam_id (str): SteamID64 del usuario.

        Returns:
            PlayerSummaryRaw | None: el perfil, o None si no existe.
        """
        data = await self._get(
            "/ISteamUser/GetPlayerSummaries/v2/",
            {"steamids": steam_id},
        )
        envelope = SteamEnvelope[PlayerSummariesRaw].model_validate(data)
        players = envelope.response.players
        return players[0] if players else None

    async def get_owned_games(self, steam_id: str) -> OwnedGamesRaw:
        """
        Consulta IPlayerService/GetOwnedGames (con nombres e iconos).

        Args:
            steam_id (str): SteamID64 del usuario.

        Returns:
            OwnedGamesRaw: biblioteca; `games` es None si es privada.
        """
        data = await self._get(
            "/IPlayerService/GetOwnedGames/v1/",
            {
                "steamid": steam_id,
                "include_appinfo": 1,
                "include_played_free_games": 1,
            },
        )
        return SteamEnvelope[OwnedGamesRaw].model_validate(data).response

    async def get_recently_played_games(self, steam_id: str) -> RecentlyPlayedGamesRaw:
        """
        Consulta IPlayerService/GetRecentlyPlayedGames (2 semanas).

        Args:
            steam_id (str): SteamID64 del usuario.

        Returns:
            RecentlyPlayedGamesRaw: juegos recientes; `total_count`
            es None si el perfil es privado.
        """
        data = await self._get(
            "/IPlayerService/GetRecentlyPlayedGames/v1/",
            {"steamid": steam_id},
        )
        envelope = SteamEnvelope[RecentlyPlayedGamesRaw]
        return envelope.model_validate(data).response
