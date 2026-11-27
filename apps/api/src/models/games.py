import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    SmallInteger,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class App(Base):
    __tablename__ = "apps"

    appid: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    icon_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    header_image_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    short_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    developers: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )

    publishers: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )

    release_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    is_free: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    platform_windows: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    platform_mac: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    platform_linux: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    is_multiplayer: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    is_coop: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    is_pvp: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    achievements_total: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    percent_positive: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    total_reviews: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    review_label: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    median_playtime_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("now()"),
        nullable=False,
    )


class PlayerGame(Base):
    __tablename__ = "player_games"

    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "players.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    appid: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "apps.appid",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    favorite: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("false"),
        nullable=False,
    )

    playtime_forever_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    playtime_2weeks_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    playtime_windows_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    playtime_mac_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    playtime_linux_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    playtime_deck_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    last_played_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    first_seen_on: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("now()"),
        nullable=False,
    )