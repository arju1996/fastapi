"""create user table

Revision ID: 99d93f4e79b8
Revises: 14b9fc43a611
Create Date: 2026-10-03 19:49:08.110039

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99d93f4e79b8'
down_revision: Union[str, Sequence[str], None] = '14b9fc43a611'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table("user",
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column("password", sa.String(), nullable=False)
        )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user")
    pass
