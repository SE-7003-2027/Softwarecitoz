from uuid import UUID

import asyncpg

from src.steam.client import ICON_URL
from src.steam.schemas import GameRaw, PlayerSummaryRaw


async def upsert_player(
    conn: asyncpg.Connection,
    auth_user_id: int,
    player: PlayerSummaryRaw,
    initialize_chaos_profile: bool = False,
) -> UUID:

    # players contiene exclusivamente información
    # perteneciente al perfil de Chaos.
    #
    # Una sincronización Steam NO debe modificar:
    #
    # user_name
    # bio
    # country_code
    # timezone
    # avatar_url

    await conn.execute(
        """
        INSERT INTO players (
            auth_user_id,
            created_at,
            updated_at
        )
        VALUES (
            $1,
            now(),
            now()
        )

        ON CONFLICT (auth_user_id)
        DO NOTHING
        """,
        auth_user_id,
    )

    player_id = await conn.fetchval(
        """
        SELECT id
        FROM players
        WHERE auth_user_id = $1
        """,
        auth_user_id,
    )

    await conn.execute(
        """
        INSERT INTO steam_profiles (
            player_id,
            steamid,
            persona_name,
            profile_url,
            avatar_url,
            community_visibility,
            steam_country_code,
            account_created_at,
            last_synced_at
        )

        VALUES (
            $1,
            $2,
            $3,
            $4,
            $5,
            $6,
            $7,
            $8,
            now()
        )

        ON CONFLICT (player_id)
        DO UPDATE SET
            steamid =
                EXCLUDED.steamid,

            persona_name =
                EXCLUDED.persona_name,

            profile_url =
                EXCLUDED.profile_url,

            avatar_url =
                EXCLUDED.avatar_url,

            community_visibility =
                EXCLUDED.community_visibility,

            steam_country_code =
                EXCLUDED.steam_country_code,

            account_created_at =
                EXCLUDED.account_created_at,

            last_synced_at =
                now()
        """,

        player_id,
        int(player.steamid),
        player.personaname,
        player.profileurl,
        player.avatarfull,
        player.communityvisibilitystate,
        player.loccountrycode,
        player.timecreated,
    )

    if initialize_chaos_profile:
        await conn.execute(
            """
            UPDATE players
            SET
                user_name = CASE
                    WHEN user_name IS NULL
                         OR btrim(user_name) = ''
                    THEN $2
                    ELSE user_name
                END,

                avatar_url = CASE
                    WHEN avatar_url IS NULL
                         OR btrim(avatar_url) = ''
                    THEN $3
                    ELSE avatar_url
                END,

                updated_at = now()

            WHERE id = $1
            """,
            player_id,
            player.personaname,
            player.avatarfull,
        )
    

    return player_id


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