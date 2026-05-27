"""Merge heads for links and charts migrations

Revision ID: 7f8d2e9c4a11
Revises: d170d90528ff, 9e0acbf8f1d2
Create Date: 2026-05-28 00:01:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "7f8d2e9c4a11"
down_revision: Union[str, Sequence[str], None] = ("d170d90528ff", "9e0acbf8f1d2")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge revisions without schema changes."""


def downgrade() -> None:
    """Split the merged heads on downgrade."""