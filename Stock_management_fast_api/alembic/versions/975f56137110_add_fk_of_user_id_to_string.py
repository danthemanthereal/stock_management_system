"""add fk of user id to string

Revision ID: 975f56137110
Revises: 2c9d11ef7424
Create Date: ... (dein Datum bleibt)

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '975f56137110'
down_revision = '2c9d11ef7424'
branch_labels = None
depends_on = None


def upgrade():
    # SQLite kann keine Spalte ändern -> Tabelle neu erstellen
    # 1. alte Tabelle umbenennen
    op.rename_table('bought_stock', 'bought_stock_old')

    # 2. neue Tabelle mit korrektem Schema erstellen (user_id als String)
    op.create_table(
        'bought_stock',
        sa.Column('id', sa.Integer, primary_key=True),  # oder UUID, je nach Modell
        sa.Column('user_id', sa.String(36), nullable=False),  # als String!
        sa.Column('name', sa.String, nullable=False),
        sa.Column('ticker', sa.String, nullable=False),
        sa.Column('bought_price', sa.Float, nullable=False),
        sa.Column('amount', sa.Float, nullable=False),
        # ... weitere Spalten, die dein Modell hat (z.B. created_at, updated_at)
    )

    # 3. Daten kopieren (falls vorhanden – bei leerer DB nicht nötig, aber sicherheitshalber)
    op.execute(
        'INSERT INTO bought_stock (id, user_id, name, ticker, bought_price, amount) SELECT id, user_id, name, ticker, bought_price, amount FROM bought_stock_old')

    # 4. alte Tabelle löschen
    op.drop_table('bought_stock_old')


def downgrade():
    # Rückgängig: wieder zu UUID-Spalte (als String bleibt es, aber wir können den Typ nicht ändern)
    op.rename_table('bought_stock', 'bought_stock_new')
    op.create_table(
        'bought_stock',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),  # gleicher Typ
        sa.Column('name', sa.String, nullable=False),
        sa.Column('ticker', sa.String, nullable=False),
        sa.Column('bought_price', sa.Float, nullable=False),
        sa.Column('amount', sa.Float, nullable=False),
    )
    op.execute('INSERT INTO bought_stock SELECT * FROM bought_stock_new')
    op.drop_table('bought_stock_new')