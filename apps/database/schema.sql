CREATE TABLE public.players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    steamid BIGINT UNIQUE,
    auth_user_id UUID UNIQUE,

    user_name TEXT,
    
    persona_name TEXT,
    profile_url TEXT,
    avatar_url TEXT,

    community_visibility SMALLINT,
    country_code TEXT,
    account_created_at TIMESTAMPTZ,
    steam_level SMALLINT,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);



CREATE TABLE public.apps (
    appid INTEGER PRIMARY KEY,

    name TEXT NOT NULL,
    header_image_url TEXT,
    short_description TEXT,

    developers TEXT[],
    publishers TEXT[],

    release_date DATE,
    is_free BOOLEAN,

    platform_windows BOOLEAN,
    platform_mac BOOLEAN,
    platform_linux BOOLEAN,

    is_multiplayer BOOLEAN,
    is_coop BOOLEAN,
    is_pvp BOOLEAN,

    achievements_total SMALLINT,

    percent_positive SMALLINT,
    total_reviews INTEGER,
    review_label TEXT,

    median_playtime_min INTEGER,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);



CREATE TABLE public.player_games (
    player_id UUID NOT NULL,
    appid INTEGER NOT NULL,

    favorite BOOLEAN NOT NULL DEFAULT FALSE,

    playtime_forever_min INTEGER,
    playtime_2weeks_min INTEGER,

    playtime_windows_min INTEGER,
    playtime_mac_min INTEGER,
    playtime_linux_min INTEGER,
    playtime_deck_min INTEGER,

    last_played_at TIMESTAMPTZ,
    first_seen_on DATE,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (player_id, appid),

    CONSTRAINT fk_player_games_player
        FOREIGN KEY (player_id)
        REFERENCES public.players(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_player_games_app
        FOREIGN KEY (appid)
        REFERENCES public.apps(appid)
        ON DELETE CASCADE
);