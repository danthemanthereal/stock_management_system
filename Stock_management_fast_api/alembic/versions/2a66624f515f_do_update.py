"""do update

Revision ID: 2a66624f515f
Revises: 0eddd377bc4b
Create Date: 2026-06-20 22:18:29.412983

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a66624f515f'
down_revision: Union[str, Sequence[str], None] = '0eddd377bc4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
