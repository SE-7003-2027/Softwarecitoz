from sqlalchemy import BigInteger, Identity, Text, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class AppUser(Base):
    __tablename__ = "app_users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )

    email: Mapped[str | None] = mapped_column(
        Text,
        unique=True,
        nullable=True,
    )

    password_hash: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    steam_id: Mapped[int | None] = mapped_column(
        BigInteger,
        unique=True,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        Text,
        server_default="active",
    )

    roles: Mapped[list[str]] = mapped_column(
        ARRAY(Text),
        server_default=text("'{user}'::text[]"),
    )