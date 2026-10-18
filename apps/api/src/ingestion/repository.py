from uuid import UUID

import asyncpg

from src.steam.client import ICON_URL
from src.steam.schemas import GameRaw, PlayerSummaryRaw


async def upsert_player(
    conn: asyncpg.Connection,
    auth_user_id: int,
    player: PlayerSummaryRaw,
) -> UUID:

    row = await conn.fetchrow(
        """
        INSERT INTO players (
            steamid,
            auth_user_id,
            user_name,
            persona_name,
            profile_url,
            avatar_url,
            community_visibility,
            country_code,
            account_created_at,
            updated_at
        )
        VALUES (
            $1, $2, $3, $3, $4, $5, $6, $7, $8, now()
        )

        ON CONFLICT (steamid)
        DO UPDATE SET
            auth_user_id = EXCLUDED.auth_user_id,
            persona_name = EXCLUDED.persona_name,
            profile_url = EXCLUDED.profile_url,
            avatar_url = EXCLUDED.avatar_url,
            community_visibility =
                EXCLUDED.community_visibility,
            country_code = EXCLUDED.country_code,
            account_created_at =
                EXCLUDED.account_created_at,
            updated_at = now()

        RETURNING id
        """,
        int(player.steamid),
        auth_user_id,
        player.personaname,
        player.profileurl,
        player.avatarfull,
        player.communityvisibilitystate,
        player.loccountrycode,
        player.timecreated,
    )

    return row["id"]


async def upsert_apps(
    conn: asyncpg.Connection,
    games: list[GameRaw],
) -> None:

    rows = []

    for game in games:
        icon_url = None

        if game.img_icon_url:
            icon_url = ICON_URL.format(
                appid=game.appid,
                icon_hash=game.img_icon_url,
            )

        rows.append(
            (
                game.appid,
                game.name,
                icon_url,
            )
        )

    if not rows:
        return

    await conn.executemany(
        """
        INSERT INTO apps (
            appid,
            name,
            icon_url,
            updated_at
        )
        VALUES ($1, $2, $3, now())

        ON CONFLICT (appid)
        DO UPDATE SET
            name = EXCLUDED.name,
            icon_url = EXCLUDED.icon_url,
            updated_at = now()
        """,
        rows,
    )


async def upsert_player_games(
    conn: asyncpg.Connection,
    player_id: UUID,
    games: list[GameRaw],
) -> None:

    rows = [
        (
            player_id,
            game.appid,
            game.playtime_forever,
            game.playtime_2weeks,
            game.playtime_windows_forever,
            game.playtime_mac_forever,
            game.playtime_linux_forever,
            game.playtime_deck_forever,
            game.rtime_last_played,
        )
        for game in games
    ]

    if not rows:
        return

    await conn.executemany(
        """
        INSERT INTO player_games (
            player_id,
            appid,
            playtime_forever_min,
            playtime_2weeks_min,
            playtime_windows_min,
            playtime_mac_min,
            playtime_linux_min,
            playtime_deck_min,
            last_played_at,
            first_seen_on,
            updated_at
        )
        VALUES (
            $1, $2, $3, $4, $5,
            $6, $7, $8, $9,
            CURRENT_DATE,
            now()
        )

        ON CONFLICT (player_id, appid)
        DO UPDATE SET
            playtime_forever_min =
                EXCLUDED.playtime_forever_min,
            playtime_2weeks_min =
                EXCLUDED.playtime_2weeks_min,
            playtime_windows_min =
                EXCLUDED.playtime_windows_min,
            playtime_mac_min =
                EXCLUDED.playtime_mac_min,
            playtime_linux_min =
                EXCLUDED.playtime_linux_min,
            playtime_deck_min =
                EXCLUDED.playtime_deck_min,
            last_played_at =
                EXCLUDED.last_played_at,
            updated_at = now()
        """,
        rows,
    )