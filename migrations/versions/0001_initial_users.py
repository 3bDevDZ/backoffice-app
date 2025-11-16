"""Initial users table

Revision ID: 0001_initial_users
Revises: None
Create Date: 2025-11-15
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_initial_users"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create table with unique constraint in column definition for SQLite compatibility
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=120), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default=sa.text("'clerk'")),
    )
    # For non-SQLite databases, also create named constraint (SQLite ignores this)
    try:
        op.create_unique_constraint("uq_users_username", "users", ["username"])
    except (NotImplementedError, ValueError):
        pass  # SQLite doesn't support this, constraint already in column definition


def downgrade() -> None:
    try:
        op.drop_constraint("uq_users_username", "users", type_="unique")
    except NotImplementedError:
        pass  # SQLite doesn't support dropping constraints this way
    op.drop_table("users")