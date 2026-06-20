"""add stock market entity for the wiki page

Revision ID: 800c758505a9
Revises: 82cc24708e23
Create Date: 2026-06-20 14:26:19.932905

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '800c758505a9'
down_revision: Union[str, Sequence[str], None] = '82cc24708e23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
