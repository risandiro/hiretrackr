"""init

Revision ID: 2aa892dfd709
Revises: 
Create Date: 2026-04-24 17:56:26.547406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2aa892dfd709'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint("users_email_key", "users", ["email"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("users_email_key", "users", type_="unique")
