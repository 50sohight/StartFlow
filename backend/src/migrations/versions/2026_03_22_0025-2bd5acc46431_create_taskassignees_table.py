"""Create TaskAssignees table

Revision ID: 2bd5acc46431
Revises: 87563ae5f1c7
Create Date: 2026-03-22 00:25:37.725556

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2bd5acc46431"
down_revision: Union[str, Sequence[str], None] = "87563ae5f1c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "task_assignees",
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("task_id", "user_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("task_assignees")
