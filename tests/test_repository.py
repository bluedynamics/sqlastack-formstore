"""FormEntry + FormEntryRepository against PostgreSQL."""

from __future__ import annotations

from sqlastack.formstore.models import FormEntry
from sqlastack.formstore.repository import FormEntryRepository


def _entry(uid="uid-1", block="form-1", **kw):
    payload = {"name": "Jane", "fields_labels": {"name": "Name"},
               "fields_order": ["name"], "fields_types": {"name": "text"}}
    return FormEntry(plone_uid=uid, block_id=block, data=payload, **kw)


def test_create_persists_jsonb_and_timestamps(pg_registry):
    with pg_registry.session_scope("fh") as session:
        repo = FormEntryRepository(session)
        created = repo.create(_entry(author="michi"))
        assert created.id is not None

    with pg_registry.session_scope("fh") as session:
        repo = FormEntryRepository(session)
        rows = repo.list_for("uid-1")
        assert len(rows) == 1
        assert rows[0].data["name"] == "Jane"
        assert rows[0].data["fields_order"] == ["name"]
        assert rows[0].author == "michi"
        assert rows[0].created_at.tzinfo is not None


def test_author_defaults_to_none_anonymous(pg_registry):
    with pg_registry.session_scope("fh") as session:
        created = FormEntryRepository(session).create(_entry())
        assert created.author is None


def test_list_for_is_scoped_and_newest_first(pg_registry):
    with pg_registry.session_scope("fh") as session:
        repo = FormEntryRepository(session)
        first = repo.create(_entry())
        second = repo.create(_entry())
        repo.create(_entry(uid="other-uid"))

    with pg_registry.session_scope("fh") as session:
        repo = FormEntryRepository(session)
        rows = repo.list_for("uid-1")
        assert [r.id for r in rows] == [second.id, first.id]
        assert repo.count_for("uid-1") == 2
        assert repo.count_for("other-uid") == 1
        assert repo.count_for("nope") == 0


def test_delete_for_is_scoped_to_uid(pg_registry):
    with pg_registry.session_scope("fh") as session:
        repo = FormEntryRepository(session)
        mine = repo.create(_entry())
        foreign = repo.create(_entry(uid="other-uid"))

    with pg_registry.session_scope("fh") as session:
        repo = FormEntryRepository(session)
        assert repo.delete_for("uid-1", foreign.id) is False  # wrong uid
        assert repo.delete_for("uid-1", mine.id) is True
        assert repo.delete_for("uid-1", mine.id) is False  # already gone

    with pg_registry.session_scope("fh") as session:
        repo = FormEntryRepository(session)
        assert repo.get_for("other-uid", foreign.id) is not None


def test_clear_for_removes_only_own_uid(pg_registry):
    with pg_registry.session_scope("fh") as session:
        repo = FormEntryRepository(session)
        repo.create(_entry())
        repo.create(_entry())
        repo.create(_entry(uid="other-uid"))

    with pg_registry.session_scope("fh") as session:
        repo = FormEntryRepository(session)
        assert repo.clear_for("uid-1") == 2

    with pg_registry.session_scope("fh") as session:
        repo = FormEntryRepository(session)
        assert repo.count_for("uid-1") == 0
        assert repo.count_for("other-uid") == 1
