"""Add stock tables: locations, stock_items, stock_movements

Revision ID: 0009_add_stock_tables
Revises: 0008_add_purchase_tables
Create Date: 2025-01-27
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


revision = "0009_add_stock_tables"
down_revision = "0008_add_purchase_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create locations table
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("capacity", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["parent_id"], ["locations.id"], name="fk_locations_parent_id"),
        sa.PrimaryKeyConstraint("id", name="pk_locations"),
        sa.UniqueConstraint("code", name="uq_locations_code")
    )
    
    # Create stock_items table
    op.create_table(
        "stock_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("variant_id", sa.Integer(), nullable=True),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("physical_quantity", sa.Numeric(precision=12, scale=3), nullable=False, server_default=sa.text("0")),
        sa.Column("reserved_quantity", sa.Numeric(precision=12, scale=3), nullable=False, server_default=sa.text("0")),
        sa.Column("min_stock", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column("max_stock", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column("reorder_point", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column("reorder_quantity", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column("valuation_method", sa.String(length=20), nullable=False, server_default=sa.text("'standard'")),
        sa.Column("last_movement_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name="fk_stock_items_product_id"),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], name="fk_stock_items_location_id"),
        sa.PrimaryKeyConstraint("id", name="pk_stock_items"),
        sa.UniqueConstraint("product_id", "variant_id", "location_id", name="uq_stock_item_product_location")
    )
    
    # Create stock_movements table
    op.create_table(
        "stock_movements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("stock_item_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("variant_id", sa.Integer(), nullable=True),
        sa.Column("location_from_id", sa.Integer(), nullable=True),
        sa.Column("location_to_id", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("reason", sa.String(length=200), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("related_document_type", sa.String(length=50), nullable=True),
        sa.Column("related_document_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["stock_item_id"], ["stock_items.id"], name="fk_stock_movements_stock_item_id"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name="fk_stock_movements_product_id"),
        sa.ForeignKeyConstraint(["location_from_id"], ["locations.id"], name="fk_stock_movements_location_from_id"),
        sa.ForeignKeyConstraint(["location_to_id"], ["locations.id"], name="fk_stock_movements_location_to_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_stock_movements_user_id"),
        sa.PrimaryKeyConstraint("id", name="pk_stock_movements")
    )


def downgrade() -> None:
    op.drop_table("stock_movements")
    op.drop_table("stock_items")
    op.drop_table("locations")






