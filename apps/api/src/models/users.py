from sqlalchemy import BigInteger, Identity, Text, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class AppUser(Base):
    __tablename__ = "app_users"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    steam_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    status: Mapped[str] = mapped_column(Text, server_default="active")
    roles: Mapped[list[str]] = mapped_column(
        ARRAY(Text), server_default=text("'{user}'::text[]")
    )
