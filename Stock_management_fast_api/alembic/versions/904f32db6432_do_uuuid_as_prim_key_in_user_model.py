"""do uuuid as prim key in user model

Revision ID: 904f32db6432
Revises: 35a722114503
Create Date: ...

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Uuid          # <-- richtiger Import (SQLAlchemy 2.0+)
import uuid

# revision identifiers, used by Alembic.
revision = '904f32db6432'
down_revision = '35a722114503'
branch_labels = None
depends_on = None

def upgrade():
    # SQLite Workaround: Neue Tabelle mit UUID-Primärschlüssel (als Uuid-Typ)
    op.create_table(
        'users_new',
        sa.Column('id', Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_name', sa.String, unique=True, nullable=False),
        sa.Column('password_hash', sa.String, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        # Falls es weitere Spalten gibt, hier ergänzen
    )

    # Daten kopieren (ohne id, weil neu generiert)
    op.execute('INSERT INTO users_new (user_name, password_hash, is_active, created_at, updated_at) SELECT user_name, password_hash, is_active, created_at, updated_at FROM users')

    op.drop_table('users')
    op.rename_table('users_new', 'users')

def downgrade():
    # Zurück zu Integer-ID
    op.create_table(
        'users_old',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_name', sa.String, unique=True, nullable=False),
        sa.Column('password_hash', sa.String, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    op.execute('INSERT INTO users_old (id, user_name, password_hash, is_active, created_at, updated_at) SELECT id, user_name, password_hash, is_active, created_at, updated_at FROM users')
    op.drop_table('users')
    op.rename_table('users_old', 'users')