"""Add products and customers tables

Revision ID: 0002_products_customers
Revises: 0001_initial_users
Create Date: 2025-11-15
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_products_customers"
down_revision = "0001_initial_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create products table with unique constraint in column definition for SQLite compatibility
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False, unique=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'active'")),
    )
    # For non-SQLite databases, create constraint separately
    try:
        op.create_unique_constraint("uq_products_code", "products", ["code"])
    except NotImplementedError:
        pass  # SQLite doesn't support this, constraint already in column definition

    # Create customers table with unique constraint in column definition for SQLite compatibility
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", sa.String(length=20), nullable=False, server_default=sa.text("'Entreprise'")),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=200), nullable=False, unique=True),
        sa.Column("category", sa.String(length=50), nullable=True),
    )
    # For non-SQLite databases, create constraint separately
    try:
        op.create_unique_constraint("uq_customers_email", "customers", ["email"])
    except NotImplementedError:
        pass  # SQLite doesn't support this, constraint already in column definition


def downgrade() -> None:
    try:
        op.drop_constraint("uq_customers_email", "customers", type_="unique")
    except NotImplementedError:
        pass  # SQLite doesn't support dropping constraints this way
    op.drop_table("customers")
    try:
        op.drop_constraint("uq_products_code", "products", type_="unique")
    except NotImplementedError:
        pass  # SQLite doesn't support dropping constraints this way
    op.drop_table("products")