"""add to user last_selcted tempalte id

Revision ID: fe642ad934a2
Revises: e1c2be431ff5
Create Date: 2026-05-24 18:27:24.685725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe642ad934a2'
down_revision: Union[str, Sequence[str], None] = 'e1c2be431ff5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Spalte mit default-Wert 1 hinzufügen (dein "Allgemein"-Profil)
    pass


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('last_selected_template_id')
