"""rm col of financial metric of category  

Revision ID: 16f4e9c9e0d9
Revises: 794637a1a808
Create Date: 2026-05-14 22:56:56.000290

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '16f4e9c9e0d9'
down_revision: Union[str, Sequence[str], None] = '794637a1a808'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('financial_metric') as batch_op:
        batch_op.drop_column('category')

def downgrade() -> None:
    with op.batch_alter_table('financial_metric') as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(), nullable=True))
