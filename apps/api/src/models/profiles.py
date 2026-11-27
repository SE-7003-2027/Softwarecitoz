import uuid
from datetime import datetime, time

from sqlalchemy import (
    BigInteger,
    CHAR,
    ForeignKey,
    Identity,
    Integer,
    SmallInteger,
    Text,
    Time,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    auth_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "app_users.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
    )

    user_name: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    country_code: Mapped[str | None] = mapped_column(
        CHAR(2),
        nullable=True,
    )

    timezone: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    avatar_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=text("now()"),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("now()"),
        nullable=False,
    )


class SteamProfile(Base):
    __tablename__ = "steam_profiles"

    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "players.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    steamid: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
    )

    persona_name: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    profile_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    avatar_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    community_visibility: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    steam_country_code: Mapped[str | None] = mapped_column(
        CHAR(2),
        nullable=True,
    )

    account_created_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    last_synced_at: Mapped[datetime] = mapped_column(
        server_default=text("now()"),
        nullable=False,
    )


class Language(Base):
    __tablename__ = "languages"

    code: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


class PlayerLanguage(Base):
    __tablename__ = "player_languages"

    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "players.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    language_code: Mapped[str] = mapped_column(
        Text,
        ForeignKey(
            "languages.code",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    level: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


class PlayerAvailability(Base):
    __tablename__ = "player_availability"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "players.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    day_of_week: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )


class Interest(Base):
    __tablename__ = "interests"

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


class PlayerInterest(Base):
    __tablename__ = "player_interests"

    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "players.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    interest_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "interests.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )