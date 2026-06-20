"""add join between user and industry

Revision ID: 0eddd377bc4b
Revises: b95b7ba267c2
Create Date: 2026-06-20 21:35:37.833591

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0eddd377bc4b'
down_revision: Union[str, Sequence[str], None] = 'b95b7ba267c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
