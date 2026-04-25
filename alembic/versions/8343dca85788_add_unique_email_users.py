"""add unique email users

Revision ID: 8343dca85788
Revises: 2aa892dfd709
Create Date: 2026-04-24 18:01:01.103952

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8343dca85788'
down_revision: Union[str, Sequence[str], None] = '2aa892dfd709'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "users_email_key",
        "users",
        ["email"],
        schema="public",
    )


def downgrade() -> None:
    op.execute('ALTER TABLE public.users DROP CONSTRAINT IF EXISTS users_email_key')