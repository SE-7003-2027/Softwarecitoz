import logging

from src.database import get_pool
from src.ingestion import repository
from src.steam.client import SteamClient

logger = logging.getLogger(__name__)


async def enqueue_express_ingest(
    steamid: str,
    auth_user_id: int,
    steam: SteamClient,
) -> None:

    profile = await steam.get_player_summary(steamid)

    if profile is None:
        logger.warning(
            "steam_profile_not_found steamid=%s",
            steamid,
        )
        return

    library = await steam.get_owned_games(steamid)

    async with get_pool().acquire() as conn:
        async with conn.transaction():

            player_id = await repository.upsert_player(
                conn,
                auth_user_id,
                profile,
            )

            if library.games is not None:
                await repository.upsert_apps(
                    conn,
                    library.games,
                )

                await repository.upsert_player_games(
                    conn,
                    player_id,
                    library.games,
                )

    logger.info(
        "express_ingest_completed steamid=%s",
        steamid,
    )