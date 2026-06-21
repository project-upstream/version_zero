"""Remove ASSOCIATE role: migrate existing rows to ANALYST.

Revision ID: a1b2c3d4e5f6
Revises: f5e1eab0d999
Create Date: 2026-06-21
"""
from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "f5e1eab0d999"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE users SET role = 'ANALYST' WHERE role = 'ASSOCIATE'")


def downgrade() -> None:
    # Original ASSOCIATE assignments are not recoverable; no-op.
    pass
