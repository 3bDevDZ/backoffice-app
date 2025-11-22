"""Add report_templates table for custom report configurations

Revision ID: 0014_add_report_templates_table
Revises: 0013_add_settings_tables
Create Date: 2025-11-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '0014_add_report_templates_table'
down_revision = '0013_add_settings_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create report_templates table
    op.create_table(
        'report_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        
        # Configuration stored as JSON
        sa.Column('columns', sa.JSON(), nullable=True),  # List of column definitions
        sa.Column('filters', sa.JSON(), nullable=True),  # Filter conditions
        sa.Column('sorting', sa.JSON(), nullable=True),  # Sort configuration
        sa.Column('grouping', sa.JSON(), nullable=True),  # Grouping configuration
        sa.Column('calculated_fields', sa.JSON(), nullable=True),  # Calculated field definitions
        
        # Metadata
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()),
        
        sa.PrimaryKeyConstraint('id', name='pk_report_templates'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_report_templates_created_by')
    )
    
    # Create index on report_type for faster queries
    op.create_index('ix_report_templates_report_type', 'report_templates', ['report_type'])
    op.create_index('ix_report_templates_created_by', 'report_templates', ['created_by'])


def downgrade() -> None:
    op.drop_index('ix_report_templates_created_by', table_name='report_templates')
    op.drop_index('ix_report_templates_report_type', table_name='report_templates')
    op.drop_table('report_templates')

