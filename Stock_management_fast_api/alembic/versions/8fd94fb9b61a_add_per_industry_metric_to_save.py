"""add per industry metric to save

Revision ID: 8fd94fb9b61a
Revises: 7719e6fcf2b8
Create Date: 2026-05-12 22:07:52.271500
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '8fd94fb9b61a'
down_revision: Union[str, Sequence[str], None] = '7719e6fcf2b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('branch_profile_metric_link') as batch_op:

        batch_op.create_foreign_key(
            'fk_branch_profile_metric_link_metric',
            'financial_metric',
            ['metric_id'],
            ['id'],
            ondelete='CASCADE'
        )

        batch_op.create_foreign_key(
            'fk_branch_profile_metric_link_profile',
            'financial_metric_branch_profile',
            ['profile_id'],
            ['id'],
            ondelete='CASCADE'
        )


def downgrade() -> None:
    with op.batch_alter_table('branch_profile_metric_link') as batch_op:

        batch_op.drop_constraint(
            'fk_branch_profile_metric_link_metric',
            type_='foreignkey'
        )

        batch_op.drop_constraint(
            'fk_branch_profile_metric_link_profile',
            type_='foreignkey'
        )