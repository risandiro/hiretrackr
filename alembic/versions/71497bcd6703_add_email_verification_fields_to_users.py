"""add email verification fields to users

Revision ID: 71497bcd6703
Revises: 8343dca85788
Create Date: 2026-04-25 11:40:24.053348

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71497bcd6703'
down_revision: Union[str, Sequence[str], None] = '8343dca85788'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('verification_sent_at', sa.DateTime(timezone=True), nullable=True))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'verification_sent_at')
    op.drop_column('users', 'verified_at')