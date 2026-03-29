"""Change to the users table: login is a unique value

Revision ID: 8a695f221974
Revises: 2bd5acc46431
Create Date: 2026-03-26 16:53:27.007196

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8a695f221974"
down_revision: Union[str, Sequence[str], None] = "2bd5acc46431"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(None, "users", ["login"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "users", type_="unique")
