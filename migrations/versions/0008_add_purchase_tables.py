"""Add purchase tables: suppliers, supplier_addresses, supplier_contacts, supplier_conditions, purchase_orders, purchase_order_lines

Revision ID: 0008_add_purchase_tables
Revises: 0007_add_customer_tables
Create Date: 2025-11-15 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '0008_add_purchase_tables'
down_revision = '0007_add_customer_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create suppliers table
    op.create_table(
        'suppliers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(length=50), nullable=False, unique=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('email', sa.String(length=200), nullable=False, unique=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('mobile', sa.String(length=20), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('company_name', sa.String(length=200), nullable=True),
        sa.Column('siret', sa.String(length=14), nullable=True, unique=True),
        sa.Column('vat_number', sa.String(length=50), nullable=True),
        sa.Column('rcs', sa.String(length=50), nullable=True),
        sa.Column('legal_form', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()),
    )

    # Create supplier_addresses table
    op.create_table(
        'supplier_addresses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('supplier_id', sa.Integer(), sa.ForeignKey('suppliers.id'), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),  # 'headquarters', 'warehouse', 'billing', 'delivery'
        sa.Column('is_default_billing', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('is_default_delivery', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('street', sa.String(length=200), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('postal_code', sa.String(length=20), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False, server_default='France'),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
    )

    # Create supplier_contacts table
    op.create_table(
        'supplier_contacts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('supplier_id', sa.Integer(), sa.ForeignKey('suppliers.id'), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('function', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('mobile', sa.String(length=20), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('receives_orders', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('receives_invoices', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
    )

    # Create supplier_conditions table
    op.create_table(
        'supplier_conditions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('supplier_id', sa.Integer(), sa.ForeignKey('suppliers.id'), unique=True, nullable=False),
        sa.Column('payment_terms_days', sa.Integer(), nullable=False, server_default=sa.text('30')),
        sa.Column('default_discount_percent', sa.Numeric(precision=5, scale=2), nullable=False, server_default=sa.text('0')),
        sa.Column('minimum_order_amount', sa.Numeric(precision=12, scale=2), nullable=False, server_default=sa.text('0')),
        sa.Column('delivery_lead_time_days', sa.Integer(), nullable=False, server_default=sa.text('7')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()),
    )

    # Create purchase_orders table
    op.create_table(
        'purchase_orders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('number', sa.String(length=50), nullable=False, unique=True),
        sa.Column('supplier_id', sa.Integer(), sa.ForeignKey('suppliers.id'), nullable=False),
        sa.Column('order_date', sa.Date(), nullable=False, server_default=func.current_date()),
        sa.Column('expected_delivery_date', sa.Date(), nullable=True),
        sa.Column('received_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('subtotal_ht', sa.Numeric(precision=12, scale=2), nullable=False, server_default=sa.text('0')),
        sa.Column('total_tax', sa.Numeric(precision=12, scale=2), nullable=False, server_default=sa.text('0')),
        sa.Column('total_ttc', sa.Numeric(precision=12, scale=2), nullable=False, server_default=sa.text('0')),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('internal_notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('confirmed_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()),
    )

    # Create purchase_order_lines table
    op.create_table(
        'purchase_order_lines',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('purchase_order_id', sa.Integer(), sa.ForeignKey('purchase_orders.id'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('discount_percent', sa.Numeric(precision=5, scale=2), nullable=False, server_default=sa.text('0')),
        sa.Column('tax_rate', sa.Numeric(precision=5, scale=2), nullable=False, server_default=sa.text('20.0')),
        sa.Column('line_total_ht', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('line_total_ttc', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('quantity_received', sa.Numeric(precision=12, scale=3), nullable=False, server_default=sa.text('0')),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
    )


def downgrade() -> None:
    op.drop_table('purchase_order_lines')
    op.drop_table('purchase_orders')
    op.drop_table('supplier_conditions')
    op.drop_table('supplier_contacts')
    op.drop_table('supplier_addresses')
    op.drop_table('suppliers')

