"""
Esquemas espejo de las respuestas crudas de la Steam Web API.

Solo se declaran los campos que usamos; el resto se ignora. Muchos
campos son opcionales porque Steam los omite en perfiles privados.
"""
from pydantic import BaseModel, ConfigDict

from src.types import UnixTimestamp


class SteamModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class SteamEnvelope[T](SteamModel):
    """Toda respuesta de la Web API viene envuelta en `response`."""

    response: T


class PlayerSummaryRaw(SteamModel):
    steamid: str
    personaname: str
    profileurl: str
    avatarfull: str
    personastate: int = 0
    communityvisibilitystate: int = 1
    profilestate: int | None = None
    realname: str | None = None
    loccountrycode: str | None = None
    timecreated: UnixTimestamp = None
    lastlogoff: UnixTimestamp = None
    gameid: str | None = None
    gameextrainfo: str | None = None


class PlayerSummariesRaw(SteamModel):
    players: list[PlayerSummaryRaw] = []


class GameRaw(SteamModel):
    appid: int
    name: str = ""
    img_icon_url: str = ""
    playtime_forever: int = 0
    playtime_2weeks: int = 0
    playtime_windows_forever: int = 0
    playtime_mac_forever: int = 0
    playtime_linux_forever: int = 0
    playtime_deck_forever: int = 0
    rtime_last_played: UnixTimestamp = None


class OwnedGamesRaw(SteamModel):
    # Si la biblioteca es privada Steam responde `{"response": {}}`,
    # por eso ambos campos pueden faltar.
    game_count: int | None = None
    games: list[GameRaw] | None = None


class RecentlyPlayedGamesRaw(SteamModel):
    total_count: int | None = None
    games: list[GameRaw] = []
