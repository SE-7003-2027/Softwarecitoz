import uuid
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, Identity, Index, LargeBinary, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class AuthSessionFamily(Base):
    __tablename__ = "auth_session_families"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("app_users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime]
    last_used_at: Mapped[datetime]
    absolute_expires_at: Mapped[datetime]
    revoked_at: Mapped[datetime | None]
    revoke_reason: Mapped[str | None] = mapped_column(Text)
    user_agent: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        Index(
            "auth_families_active_by_user",
            "user_id",
            postgresql_where=text("revoked_at IS NULL"),
        ),
    )


class AuthRefreshToken(Base):
    __tablename__ = "auth_refresh_tokens"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    family_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth_session_families.id", ondelete="CASCADE")
    )
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("auth_refresh_tokens.id", ondelete="SET NULL")
    )
    token_hash: Mapped[bytes] = mapped_column(LargeBinary, unique=True)
    issued_at: Mapped[datetime]
    expires_at: Mapped[datetime]
    used_at: Mapped[datetime | None]
