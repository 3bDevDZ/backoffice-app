"""Add locale field to users table

Revision ID: 0003_add_user_locale
Revises: 0002_products_customers
Create Date: 2025-01-27
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_add_user_locale"
down_revision = "0002_products_customers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use batch mode for SQLite compatibility when adding columns
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("locale", sa.String(length=5), nullable=False, server_default="fr"))


def downgrade() -> None:
    op.drop_column("users", "locale")

