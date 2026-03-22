"""Create Users table

Revision ID: 7874f74019d0
Revises:
Create Date: 2026-03-21 15:44:28.974018

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7874f74019d0"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("login", sa.VARCHAR(length=100), nullable=False),
        sa.Column("password_hash", sa.VARCHAR(length=255), nullable=False),
        sa.Column("fullname", sa.VARCHAR(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
