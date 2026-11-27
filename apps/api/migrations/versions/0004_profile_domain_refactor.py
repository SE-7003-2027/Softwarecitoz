"""separate Chaos profile data from Steam data

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-09 21:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004"
down_revision: Union[str, Sequence[str], None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # ---------------------------------------------------------
    # 1. Nuevos campos propios del perfil de Chaos
    # ---------------------------------------------------------

    op.add_column(
        "players",
        sa.Column(
            "bio",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "players",
        sa.Column(
            "timezone",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "players",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Toda cuenta Chaos debe tener un perfil players.
    op.execute(
        """
        INSERT INTO players (
            auth_user_id,
            created_at,
            updated_at
        )
        SELECT
            u.id,
            now(),
            now()
        FROM app_users AS u
        WHERE NOT EXISTS (
            SELECT 1
            FROM players AS p
            WHERE p.auth_user_id = u.id
        )
        """
    )

    # Evitamos convertir auth_user_id a NOT NULL si existen
    # perfiles huérfanos.
    orphan_count = bind.execute(
        sa.text(
            """
            SELECT count(*)
            FROM players
            WHERE auth_user_id IS NULL
            """
        )
    ).scalar_one()

    if orphan_count:
        raise RuntimeError(
            "Hay registros en players sin auth_user_id. "
            "Asignalos a una cuenta o eliminalos antes "
            "de aplicar la migracion 0004."
        )

    op.alter_column(
        "players",
        "auth_user_id",
        existing_type=sa.BigInteger(),
        nullable=False,
    )

    # ---------------------------------------------------------
    # 2. Perfil Steam separado
    # ---------------------------------------------------------

    op.create_table(
        "steam_profiles",

        sa.Column(
            "player_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "steamid",
            sa.BigInteger(),
            nullable=False,
        ),

        sa.Column(
            "persona_name",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "profile_url",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "avatar_url",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "community_visibility",
            sa.SmallInteger(),
            nullable=True,
        ),

        sa.Column(
            "steam_country_code",
            sa.CHAR(length=2),
            nullable=True,
        ),

        sa.Column(
            "account_created_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "last_synced_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["player_id"],
            ["players.id"],
            name="fk_steam_profiles_player_id_players",
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "player_id",
            name="pk_steam_profiles",
        ),

        sa.UniqueConstraint(
            "steamid",
            name="uq_steam_profiles_steamid",
        ),
    )

    # Copiamos la información Steam que actualmente vive en players.
    op.execute(
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
        SELECT
            p.id,
            p.steamid,
            p.persona_name,
            p.profile_url,
            p.avatar_url,
            p.community_visibility,

            CASE
                WHEN p.country_code IS NULL
                    THEN NULL
                ELSE left(p.country_code, 2)::char(2)
            END,

            p.account_created_at,
            p.updated_at

        FROM players AS p

        WHERE p.steamid IS NOT NULL

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
                EXCLUDED.last_synced_at
        """
    )

    # app_users todavía contiene steam_id debido a 0002.
    # Conservamos también esas vinculaciones.
    op.execute(
        """
        INSERT INTO steam_profiles (
            player_id,
            steamid,
            last_synced_at
        )

        SELECT
            p.id,
            u.steam_id,
            now()

        FROM app_users AS u

        JOIN players AS p
            ON p.auth_user_id = u.id

        WHERE u.steam_id IS NOT NULL

        ON CONFLICT (player_id)
        DO UPDATE SET
            steamid = EXCLUDED.steamid,
            last_synced_at = now()
        """
    )

    # Hasta ahora avatar_url y country_code de players
    # provenían de Steam.
    #
    # Ahora estos campos representan datos propios de Chaos.
    # Como ya copiamos los antiguos a steam_profiles,
    # los limpiamos.
    op.execute(
        """
        UPDATE players
        SET
            avatar_url = NULL,
            country_code = NULL
        """
    )

    op.alter_column(
        "players",
        "country_code",
        existing_type=sa.Text(),
        type_=sa.CHAR(length=2),
        existing_nullable=True,
        postgresql_using="country_code::char(2)",
    )

    # ---------------------------------------------------------
    # 3. Eliminamos de players los campos exclusivos de Steam
    # ---------------------------------------------------------

    op.drop_column(
        "players",
        "steam_level",
    )

    op.drop_column(
        "players",
        "account_created_at",
    )

    op.drop_column(
        "players",
        "community_visibility",
    )

    op.drop_column(
        "players",
        "profile_url",
    )

    op.drop_column(
        "players",
        "persona_name",
    )

    op.drop_column(
        "players",
        "steamid",
    )

    # Steam ya no forma parte de app_users.
    op.drop_column(
        "app_users",
        "steam_id",
    )

    # ---------------------------------------------------------
    # 4. Idiomas
    # ---------------------------------------------------------

    op.create_table(
        "languages",

        sa.Column(
            "code",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "name",
            sa.Text(),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint(
            "code",
            name="pk_languages",
        ),
    )

    op.create_table(
        "player_languages",

        sa.Column(
            "player_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "language_code",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "level",
            sa.Text(),
            nullable=True,
        ),

        sa.ForeignKeyConstraint(
            ["player_id"],
            ["players.id"],
            name="fk_player_languages_player_id_players",
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["language_code"],
            ["languages.code"],
            name="fk_player_languages_language_code_languages",
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "player_id",
            "language_code",
            name="pk_player_languages",
        ),
    )

    # ---------------------------------------------------------
    # 5. Disponibilidad
    # ---------------------------------------------------------

    op.create_table(
        "player_availability",

        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text(
                "gen_random_uuid()"
            ),
            nullable=False,
        ),

        sa.Column(
            "player_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "day_of_week",
            sa.SmallInteger(),
            nullable=False,
        ),

        sa.Column(
            "start_time",
            sa.Time(),
            nullable=False,
        ),

        sa.Column(
            "end_time",
            sa.Time(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["player_id"],
            ["players.id"],
            name="fk_player_availability_player_id_players",
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "id",
            name="pk_player_availability",
        ),
    )

    # ---------------------------------------------------------
    # 6. Intereses generales
    # ---------------------------------------------------------

    op.create_table(
        "interests",

        sa.Column(
            "id",
            sa.Integer(),
            sa.Identity(always=False),
            nullable=False,
        ),

        sa.Column(
            "name",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "category",
            sa.Text(),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint(
            "id",
            name="pk_interests",
        ),
    )

    op.create_table(
        "player_interests",

        sa.Column(
            "player_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "interest_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["player_id"],
            ["players.id"],
            name="fk_player_interests_player_id_players",
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["interest_id"],
            ["interests.id"],
            name="fk_player_interests_interest_id_interests",
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "player_id",
            "interest_id",
            name="pk_player_interests",
        ),
    )


def downgrade() -> None:
    # Restauramos steam_id en app_users.
    op.add_column(
        "app_users",
        sa.Column(
            "steam_id",
            sa.BigInteger(),
            nullable=True,
        ),
    )

    op.create_unique_constraint(
        "uq_app_users_steam_id",
        "app_users",
        ["steam_id"],
    )

    op.execute(
        """
        UPDATE app_users AS u

        SET steam_id = sp.steamid

        FROM players AS p

        JOIN steam_profiles AS sp
            ON sp.player_id = p.id

        WHERE p.auth_user_id = u.id
        """
    )

    # Tablas nuevas.
    op.drop_table("player_interests")
    op.drop_table("interests")
    op.drop_table("player_availability")
    op.drop_table("player_languages")
    op.drop_table("languages")

    # Restauramos la estructura antigua de players.
    op.add_column(
        "players",
        sa.Column(
            "steamid",
            sa.BigInteger(),
            nullable=True,
        ),
    )

    op.add_column(
        "players",
        sa.Column(
            "persona_name",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "players",
        sa.Column(
            "profile_url",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "players",
        sa.Column(
            "community_visibility",
            sa.SmallInteger(),
            nullable=True,
        ),
    )

    op.add_column(
        "players",
        sa.Column(
            "account_created_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "players",
        sa.Column(
            "steam_level",
            sa.SmallInteger(),
            nullable=True,
        ),
    )

    op.create_unique_constraint(
        "uq_players_steamid",
        "players",
        ["steamid"],
    )

    op.alter_column(
        "players",
        "country_code",
        existing_type=sa.CHAR(length=2),
        type_=sa.Text(),
        existing_nullable=True,
        postgresql_using="country_code::text",
    )

    op.execute(
        """
        UPDATE players AS p

        SET
            steamid =
                sp.steamid,

            persona_name =
                sp.persona_name,

            profile_url =
                sp.profile_url,

            avatar_url =
                sp.avatar_url,

            community_visibility =
                sp.community_visibility,

            country_code =
                sp.steam_country_code,

            account_created_at =
                sp.account_created_at

        FROM steam_profiles AS sp

        WHERE sp.player_id = p.id
        """
    )

    op.drop_table(
        "steam_profiles"
    )

    op.alter_column(
        "players",
        "auth_user_id",
        existing_type=sa.BigInteger(),
        nullable=True,
    )

    op.drop_column(
        "players",
        "created_at",
    )

    op.drop_column(
        "players",
        "timezone",
    )

    op.drop_column(
        "players",
        "bio",
    )