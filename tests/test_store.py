"""SQLFormDataStore against PostgreSQL via the process-wide registry."""

from __future__ import annotations

from sqlastack.formstore.store import SQLFormDataStore
from sqlastack.plone import get_registry
from sqlastack.plone import reset_registry
import datetime
import json
import pytest
import transaction


BLOCKS = {
    "form-1": {
        "@type": "form",
        "store": True,
        "subblocks": [
            {"field_id": "name", "label": "Name", "field_type": "text"},
            {"field_id": "email", "label": "E-Mail", "field_type": "from"},
            {"field_id": "cv", "label": "CV", "field_type": "attachment"},
        ],
    },
    "text-1": {"@type": "text"},
}

SUBMISSION = [
    {"field_id": "name", "value": "Jane"},
    {"field_id": "email", "value": "jane@example.org"},
    {"field_id": "cv", "value": {"data": "...", "encoding": "base64"}},
    {"field_id": "sneaky", "value": "not in form"},
]


class FakeContext:
    def __init__(self, uid: str, blocks: dict) -> None:
        self._uid = uid
        self.blocks = blocks

    def UID(self) -> str:
        return self._uid

    def absolute_url(self) -> str:
        return f"http://nohost/plone/{self._uid}"


class FakeRequest(dict):
    def __init__(self, body: dict | None = None) -> None:
        super().__init__()
        self.form: dict = {}
        if body is not None:
            self["BODY"] = json.dumps(body)


@pytest.fixture
def forms_env(pg_url, pg_engine, monkeypatch):
    monkeypatch.setenv("SQLASTACK_FORMS_URL", pg_url)
    reset_registry()
    yield
    transaction.abort()
    reset_registry()


@pytest.fixture
def store(forms_env):
    return SQLFormDataStore(
        FakeContext("uid-1", BLOCKS), FakeRequest({"block_id": "form-1"})
    )


def test_add_persists_and_returns_id(store):
    record_id = store.add(SUBMISSION)
    transaction.commit()
    assert isinstance(record_id, int)

    with get_registry().session_scope("forms") as session:
        from sqlastack.formstore.repository import FormEntryRepository

        rows = FormEntryRepository(session).list_for("uid-1")
        assert len(rows) == 1
        assert rows[0].data["name"] == "Jane"


def test_add_skips_attachment_and_unknown_fields(store):
    store.add(SUBMISSION)
    transaction.commit()
    [record] = store.search()
    assert "cv" not in record.attrs
    assert "sneaky" not in record.attrs
    assert record.attrs["fields_order"] == ["name", "email"]
    assert record.attrs["fields_labels"] == {"name": "Name", "email": "E-Mail"}
    assert record.attrs["fields_types"] == {"name": "text", "email": "from"}


def test_add_unknown_block_returns_none(forms_env):
    store = SQLFormDataStore(
        FakeContext("uid-1", BLOCKS), FakeRequest({"block_id": "missing"})
    )
    assert store.add(SUBMISSION) is None


def test_author_defaults_to_anonymous_and_can_be_user(store, monkeypatch):
    store.add(SUBMISSION)
    monkeypatch.setattr(SQLFormDataStore, "_current_userid", lambda self: "michi")
    store.add(SUBMISSION)
    transaction.commit()

    with get_registry().session_scope("forms") as session:
        from sqlastack.formstore.repository import FormEntryRepository

        authors = {r.author for r in FormEntryRepository(session).list_for("uid-1")}
        assert authors == {None, "michi"}


def test_search_record_contract(store):
    store.add(SUBMISSION)
    transaction.commit()
    [record] = store.search()
    assert record.intid is not None
    assert record.attrs["block_id"] == "form-1"
    # formsupport compares attrs["date"] < datetime.now() (naive!) — spec §3
    assert record.attrs["date"].tzinfo is None
    assert record.attrs["date"] <= datetime.datetime.now()
    assert record.attrs["name"] == "Jane"


def test_search_is_scoped_to_context_uid(store, forms_env):
    store.add(SUBMISSION)
    other = SQLFormDataStore(
        FakeContext("uid-2", BLOCKS), FakeRequest({"block_id": "form-1"})
    )
    other.add(SUBMISSION)
    transaction.commit()
    assert len(store.search()) == 1
    assert store.length() == 1


def test_delete_and_clear(store, forms_env):
    first = store.add(SUBMISSION)
    store.add(SUBMISSION)
    other = SQLFormDataStore(
        FakeContext("uid-2", BLOCKS), FakeRequest({"block_id": "form-1"})
    )
    other.add(SUBMISSION)
    transaction.commit()

    store.delete(first)
    transaction.commit()
    assert store.length() == 1

    store.clear()
    transaction.commit()
    assert store.length() == 0
    assert other.length() == 1  # anderes Objekt unberührt


def test_two_requests_no_bleed(store):
    from sqlastack.plone import close_zope_sessions

    store.add(SUBMISSION)
    transaction.abort()  # Request 1 scheitert
    close_zope_sessions(None)

    assert store.length() == 0
    transaction.abort()
