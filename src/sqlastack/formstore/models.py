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

    ``data`` holds the field values plus the soup-store-compatible metadata
    keys ``fields_labels``/``fields_order``/``fields_types`` (spec §5) —
    everything formsupport's listing/CSV endpoints expect in ``record.attrs``
    except ``block_id`` and ``date``, which live as real columns.
    """

    __tablename__ = "formstore_entry"
    __table_args__ = (Index("ix_formstore_entry_form", "plone_uid", "block_id"),)

    id: int | None = Field(default=None, primary_key=True, sa_type=BigInteger)
    plone_uid: str = Field(max_length=36)
    block_id: str = Field(max_length=64)
    author: str | None = Field(default=None, max_length=255)
    data: dict = Field(sa_type=JSONB)
