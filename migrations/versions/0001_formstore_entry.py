"""create formstore_entry

Revision ID: 0001
Revises:
Create Date: 2026-09-18
"""

from __future__ import annotations

from alembic import op
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "formstore_entry",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("plone_uid", sa.String(36), nullable=False),
        sa.Column("block_id", sa.String(64), nullable=False),
        sa.Column("author", sa.String(255), nullable=True),
        sa.Column("data", postgresql.JSONB(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_formstore_entry_form", "formstore_entry", ["plone_uid", "block_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_formstore_entry_form", table_name="formstore_entry")
    op.drop_table("formstore_entry")
