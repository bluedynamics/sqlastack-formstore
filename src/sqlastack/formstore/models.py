"""SQLModel models owned by sqlastack-formstore."""

from __future__ import annotations

from sqlalchemy import BigInteger
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlastack.core.mixins import TimestampMixin
from sqlmodel import Field
from sqlmodel import SQLModel


class FormEntry(TimestampMixin, SQLModel, table=True):
    """One stored form submission.

    ``data`` holds ONLY the submitted field values (field_id -> value). The
    per-submission schema snapshot lives in its own columns:
    ``fields_labels``/``fields_types``/``fields_order`` — snapshots, because
    the form definition can change over time and even the submitted field
    subset varies per submission. The formsupport read contract (soup-style
    ``record.attrs``) is reassembled from all of these plus ``block_id`` and
    ``created_at`` in ``store.SQLRecord``.
    """

    __tablename__ = "formstore_entry"
    __table_args__ = (Index("ix_formstore_entry_form", "plone_uid", "block_id"),)

    id: int | None = Field(default=None, primary_key=True, sa_type=BigInteger)
    plone_uid: str = Field(max_length=36)
    block_id: str = Field(max_length=64)
    author: str | None = Field(default=None, max_length=255)
    data: dict = Field(sa_type=JSONB)
    fields_labels: dict = Field(sa_type=JSONB)
    fields_types: dict = Field(sa_type=JSONB)
    fields_order: list = Field(sa_type=JSONB)
