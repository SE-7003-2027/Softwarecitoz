from typing import Annotated

from fastapi import Depends, Request

from src.steam.client import SteamClient


def get_steam_client(request: Request) -> SteamClient:
    """Regresa el SteamClient creado en el lifespan de la app."""
    return request.app.state.steam_client


SteamClientDep = Annotated[SteamClient, Depends(get_steam_client)]
