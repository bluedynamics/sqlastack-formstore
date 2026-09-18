"""Repository for FormEntry — flush-only, never commits.

Deletion goes through ORM instances (session.delete + flush), NOT through a
Core DELETE statement: zope.sqlalchemy only commits sessions that were marked
changed by a flush, so a bulk statement would be silently rolled back at
``transaction.commit()`` unless mark_changed were called — a zope coupling
this module deliberately avoids.
"""

from __future__ import annotations

from collections.abc import Sequence
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlastack.core.exceptions import translate_exception
from sqlastack.formstore.models import FormEntry
import sqlalchemy.exc


class FormEntryRepository:
    """CRUD for FormEntry, scoped by plone_uid. Committing is the caller's job."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, entry: FormEntry) -> FormEntry:
        """Add and flush; primary key is populated via INSERT..RETURNING.

        Raises translated sqlastack exceptions on flush failure (same types
        in standalone and zope mode).
        """
        self.session.add(entry)
        try:
            self.session.flush()
        except sqlalchemy.exc.SQLAlchemyError as exc:
            raise translate_exception(exc) from exc
        return entry

    def list_for(self, plone_uid: str) -> Sequence[FormEntry]:
        stmt = (
            select(FormEntry)
            .where(FormEntry.plone_uid == plone_uid)
            .order_by(desc(FormEntry.created_at), desc(FormEntry.id))
        )
        return self.session.scalars(stmt).all()

    def count_for(self, plone_uid: str) -> int:
        stmt = (
            select(func.count())
            .select_from(FormEntry)
            .where(FormEntry.plone_uid == plone_uid)
        )
        return int(self.session.scalar(stmt) or 0)

    def get_for(self, plone_uid: str, entry_id: int) -> FormEntry | None:
        entry = self.session.get(FormEntry, entry_id)
        if entry is None or entry.plone_uid != plone_uid:
            return None
        return entry

    def delete_for(self, plone_uid: str, entry_id: int) -> bool:
        entry = self.get_for(plone_uid, entry_id)
        if entry is None:
            return False
        self.session.delete(entry)
        self.session.flush()
        return True

    def clear_for(self, plone_uid: str) -> int:
        entries = self.list_for(plone_uid)
        for entry in entries:
            self.session.delete(entry)
        self.session.flush()
        return len(entries)
