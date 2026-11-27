"""adopt existing domain tables into alembic

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-09 21:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003"
down_revision: Union[str, Sequence[str], None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Registra dentro de Alembic las tablas de dominio que originalmente
    fueron creadas mediante apps/database/schema.sql.

    En la BD actual de Supabase ya existen, por lo que no se recrean.

    En una BD nueva, esta migración crea la estructura anterior para que
    la siguiente migración pueda transformarla al nuevo modelo.
    """

    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())

    if "players" not in tables:
        op.create_table(
            "players",
            sa.Column(
                "id",
                sa.UUID(),
                server_default=sa.text("gen_random_uuid()"),
                nullable=False,
            ),
            sa.Column("steamid", sa.BigInteger(), nullable=True),
            sa.Column("auth_user_id", sa.BigInteger(), nullable=True),
            sa.Column("user_name", sa.Text(), nullable=True),
            sa.Column("persona_name", sa.Text(), nullable=True),
            sa.Column("profile_url", sa.Text(), nullable=True),
            sa.Column("avatar_url", sa.Text(), nullable=True),
            sa.Column(
                "community_visibility",
                sa.SmallInteger(),
                nullable=True,
            ),
            sa.Column("country_code", sa.Text(), nullable=True),
            sa.Column(
                "account_created_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
            sa.Column(
                "steam_level",
                sa.SmallInteger(),
                nullable=True,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["auth_user_id"],
                ["app_users.id"],
                name="fk_players_auth_user",
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint(
                "id",
                name="pk_players",
            ),
            sa.UniqueConstraint(
                "steamid",
                name="uq_players_steamid",
            ),
            sa.UniqueConstraint(
                "auth_user_id",
                name="uq_players_auth_user_id",
            ),
        )

    if "apps" not in tables:
        op.create_table(
            "apps",
            sa.Column("appid", sa.Integer(), nullable=False),
            sa.Column("name", sa.Text(), nullable=False),
            sa.Column("icon_url", sa.Text(), nullable=True),
            sa.Column("header_image_url", sa.Text(), nullable=True),
            sa.Column("short_description", sa.Text(), nullable=True),
            sa.Column(
                "developers",
                sa.ARRAY(sa.Text()),
                nullable=True,
            ),
            sa.Column(
                "publishers",
                sa.ARRAY(sa.Text()),
                nullable=True,
            ),
            sa.Column("release_date", sa.Date(), nullable=True),
            sa.Column("is_free", sa.Boolean(), nullable=True),
            sa.Column(
                "platform_windows",
                sa.Boolean(),
                nullable=True,
            ),
            sa.Column(
                "platform_mac",
                sa.Boolean(),
                nullable=True,
            ),
            sa.Column(
                "platform_linux",
                sa.Boolean(),
                nullable=True,
            ),
            sa.Column(
                "is_multiplayer",
                sa.Boolean(),
                nullable=True,
            ),
            sa.Column(
                "is_coop",
                sa.Boolean(),
                nullable=True,
            ),
            sa.Column(
                "is_pvp",
                sa.Boolean(),
                nullable=True,
            ),
            sa.Column(
                "achievements_total",
                sa.SmallInteger(),
                nullable=True,
            ),
            sa.Column(
                "percent_positive",
                sa.SmallInteger(),
                nullable=True,
            ),
            sa.Column(
                "total_reviews",
                sa.Integer(),
                nullable=True,
            ),
            sa.Column(
                "review_label",
                sa.Text(),
                nullable=True,
            ),
            sa.Column(
                "median_playtime_min",
                sa.Integer(),
                nullable=True,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint(
                "appid",
                name="pk_apps",
            ),
        )

    tables = set(sa.inspect(bind).get_table_names())

    if "player_games" not in tables:
        op.create_table(
            "player_games",
            sa.Column(
                "player_id",
                sa.UUID(),
                nullable=False,
            ),
            sa.Column(
                "appid",
                sa.Integer(),
                nullable=False,
            ),
            sa.Column(
                "favorite",
                sa.Boolean(),
                server_default=sa.text("false"),
                nullable=False,
            ),
            sa.Column(
                "playtime_forever_min",
                sa.Integer(),
                nullable=True,
            ),
            sa.Column(
                "playtime_2weeks_min",
                sa.Integer(),
                nullable=True,
            ),
            sa.Column(
                "playtime_windows_min",
                sa.Integer(),
                nullable=True,
            ),
            sa.Column(
                "playtime_mac_min",
                sa.Integer(),
                nullable=True,
            ),
            sa.Column(
                "playtime_linux_min",
                sa.Integer(),
                nullable=True,
            ),
            sa.Column(
                "playtime_deck_min",
                sa.Integer(),
                nullable=True,
            ),
            sa.Column(
                "last_played_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
            sa.Column(
                "first_seen_on",
                sa.Date(),
                nullable=True,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["player_id"],
                ["players.id"],
                name="fk_player_games_player",
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["appid"],
                ["apps.appid"],
                name="fk_player_games_app",
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint(
                "player_id",
                "appid",
                name="pk_player_games",
            ),
        )


def downgrade() -> None:
    raise RuntimeError(
        "0003 es una migracion baseline. "
        "No puede revertirse automaticamente de forma segura."
    )