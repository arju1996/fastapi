"""create tweet table

Revision ID: 14b9fc43a611
Revises: 
Create Date: 2026-10-03 17:30:26.394730

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14b9fc43a611'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tweet",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(), nullable=False)
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tweet")
    pass
