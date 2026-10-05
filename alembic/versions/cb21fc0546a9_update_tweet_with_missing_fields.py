"""update tweet with missing fields

Revision ID: cb21fc0546a9
Revises: 99d93f4e79b8
Create Date: 2026-10-03 20:13:39.857650

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb21fc0546a9'
down_revision: Union[str, Sequence[str], None] = '99d93f4e79b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("tweet", sa.Column('content', sa.String(), nullable=False))
    op.add_column("tweet", sa.Column('validated',sa.Boolean(), nullable=False, server_default=sa.text("False")))
    op.add_column("tweet", sa.Column('media_url',sa.String(), nullable=True))
    op.add_column("tweet", sa.Column('owner_id',sa.Integer(), nullable=False))
    op.add_column("tweet", sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.create_foreign_key("post_users_fk", source_table="tweet", referent_table="user", local_cols=["owner_id"], remote_cols=["id"], ondelete="CASCADE")
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("post_users_fk", "tweet")
    op.drop_column("tweet", "content")
    op.drop_column("tweet", "validated")
    op.drop_column("tweet", "media_url")
    op.drop_column("tweet", "owner_id")
    op.drop_column("tweet", "created_at")
    pass
