"""Add outbox_events table

Revision ID: 0004_add_outbox_events
Revises: 0003_add_user_locale
Create Date: 2025-01-28
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0004_add_outbox_events'
down_revision = '0003_add_user_locale'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'outbox_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_type', sa.String(length=255), nullable=False),
        sa.Column('event_data', sa.Text(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('occurred_on', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('is_processed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('processed_on', sa.DateTime(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('error_message', sa.Text(), nullable=True),
    )
    op.create_index('idx_outbox_events_is_processed', 'outbox_events', ['is_processed', 'occurred_on'])


def downgrade() -> None:
    op.drop_index('idx_outbox_events_is_processed', table_name='outbox_events')
    op.drop_table('outbox_events')

