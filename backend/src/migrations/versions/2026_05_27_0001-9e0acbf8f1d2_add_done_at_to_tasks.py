"""Add done_at to tasks

Revision ID: 9e0acbf8f1d2
Revises: 8a695f221974
Create Date: 2026-05-27 00:01:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9e0acbf8f1d2"
down_revision: Union[str, Sequence[str], None] = "8a695f221974"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "tasks",
        sa.Column("done_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )

    op.execute(
        """
        UPDATE tasks AS t
        SET done_at = COALESCE(t.done_at, t.updated_at)
        FROM (
            SELECT DISTINCT ON (project_id) id, project_id
            FROM columns
            ORDER BY project_id, position DESC, id DESC
        ) AS last_columns
        WHERE t.column_id = last_columns.id
          AND t.done_at IS NULL
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("tasks", "done_at")