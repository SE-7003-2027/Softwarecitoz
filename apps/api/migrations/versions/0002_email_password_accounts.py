"""add email password accounts

Revision ID: 40f047864c30
Revises: 0001
Create Date: 2026-11-07 18:18:13.479939

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40f047864c30'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "app_users",
        sa.Column("email", sa.Text(), nullable=True),
    )

    op.add_column(
        "app_users",
        sa.Column("password_hash", sa.Text(), nullable=True),
    )

    op.alter_column(
        "app_users",
        "steam_id",
        existing_type=sa.BigInteger(),
        nullable=True,
    )

    op.create_unique_constraint(
        "uq_app_users_email",
        "app_users",
        ["email"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_app_users_email",
        "app_users",
        type_="unique",
    )

    op.alter_column(
        "app_users",
        "steam_id",
        existing_type=sa.BigInteger(),
        nullable=False,
    )

    op.drop_column("app_users", "password_hash")
    op.drop_column("app_users", "email")