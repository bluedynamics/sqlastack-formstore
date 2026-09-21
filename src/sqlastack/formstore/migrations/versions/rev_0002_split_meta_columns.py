"""split fields_labels/fields_types/fields_order out of data

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-21
"""

from __future__ import annotations

from alembic import op
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

_META = ("fields_labels", "fields_types", "fields_order")


def upgrade() -> None:
    op.add_column(
        "formstore_entry",
        sa.Column(
            "fields_labels",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column(
        "formstore_entry",
        sa.Column(
            "fields_types",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.add_column(
        "formstore_entry",
        sa.Column(
            "fields_order",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    # Backfill: Meta-Keys aus data in die Spalten ziehen, data bereinigen
    op.execute(
        """
        UPDATE formstore_entry SET
          fields_labels = coalesce(data->'fields_labels', '{}'::jsonb),
          fields_types = coalesce(data->'fields_types', '{}'::jsonb),
          fields_order = coalesce(data->'fields_order', '[]'::jsonb),
          data = data - 'fields_labels' - 'fields_types' - 'fields_order'
        """
    )
    # server_default nur fürs Backfill — Modell definiert keinen
    for column in _META:
        op.alter_column("formstore_entry", column, server_default=None)


def downgrade() -> None:
    op.execute(
        """
        UPDATE formstore_entry SET
          data = data || jsonb_build_object(
            'fields_labels', fields_labels,
            'fields_types', fields_types,
            'fields_order', fields_order
          )
        """
    )
    for column in _META:
        op.drop_column("formstore_entry", column)
