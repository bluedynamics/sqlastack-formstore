"""FormBlockDataStore (plone.formblock) against PostgreSQL via the registry."""

from __future__ import annotations

from sqlastack.formstore.store_formblock import FormBlockDataStore
from sqlastack.plone import get_registry
from test_store import FakeContext
from test_store import FakeRequest
import datetime
import pytest
import transaction


BLOCKS = {
    "form-id": {
        "@type": "schemaForm",
        "store": True,
        "schema": {
            "fieldsets": [{"id": "default", "fields": ["name", "message", "cv"]}],
            "properties": {
                "name": {"title": "Name", "type": "string"},
                "message": {
                    "title": "Message",
                    "type": "string",
                    "factory": "textarea",
                },
                "cv": {"title": "CV", "type": "object", "factory": "File Upload"},
            },
            "required": ["name"],
        },
    },
    "form-old": {
        "@type": "form",
        "store": True,
        "subblocks": [{"field_id": "name", "label": "Name", "field_type": "text"}],
    },
    "text-1": {"@type": "text"},
}

# shape produced by plone.formblock's FormSubmissionContext.get_records()
SUBMISSION = [
    {"field_id": "name", "value": "Jane", "label": "Name"},
    {"field_id": "message", "value": "hello", "label": "Message"},
    {"field_id": "cv", "value": {"data": "...", "encoding": "base64"}, "label": "CV"},
    {"field_id": "sneaky", "value": "not in form", "label": "sneaky"},
]


@pytest.fixture
def store(forms_env):
    return FormBlockDataStore(
        FakeContext("uid-1", BLOCKS), FakeRequest({"block_id": "form-id"})
    )


def test_add_persists_and_returns_id(store):
    record_id = store.add(SUBMISSION)
    transaction.commit()
    assert isinstance(record_id, int)

    with get_registry().session_scope("forms") as session:
        from sqlastack.formstore.repository import FormEntryRepository

        rows = FormEntryRepository(session).list_for("uid-1")
        assert len(rows) == 1
        assert rows[0].data == {"name": "Jane", "message": "hello"}
        assert rows[0].author is None  # anonymous outside Zope
        assert rows[0].fields_labels == {"name": "Name", "message": "Message"}
        assert rows[0].fields_order == ["name", "message"]
        # factory wins over JSON-schema type when present
        assert rows[0].fields_types == {"name": "string", "message": "textarea"}


def test_add_unknown_block_returns_none(forms_env):
    store = FormBlockDataStore(
        FakeContext("uid-1", BLOCKS), FakeRequest({"block_id": "missing"})
    )
    assert store.add(SUBMISSION) is None


def test_add_ignores_formsupport_style_block(forms_env):
    # a formsupport "form" block is not ours: only @type == "schemaForm" counts
    store = FormBlockDataStore(
        FakeContext("uid-1", BLOCKS), FakeRequest({"block_id": "form-old"})
    )
    assert store.add(SUBMISSION) is None


def test_search_record_contract(store):
    store.add(SUBMISSION)
    transaction.commit()
    [record] = store.search()
    assert record.intid is not None
    assert record.attrs["name"] == "Jane"
    assert record.attrs["block_id"] == "form-id"
    assert record.attrs["fields_labels"] == {"name": "Name", "message": "Message"}
    assert record.attrs["fields_order"] == ["name", "message"]
    # formblock's expand_records only skips fields_labels/fields_order —
    # fields_types in attrs would be rendered as a form field
    assert "fields_types" not in record.attrs
    # formblock compares attrs["date"] < datetime.now() (naive!)
    assert record.attrs["date"].tzinfo is None
    assert record.attrs["date"] <= datetime.datetime.now()


def test_length_delete_clear_scoped_to_uid(store, forms_env):
    first = store.add(SUBMISSION)
    store.add(SUBMISSION)
    other = FormBlockDataStore(
        FakeContext("uid-2", BLOCKS), FakeRequest({"block_id": "form-id"})
    )
    other.add(SUBMISSION)
    transaction.commit()

    assert store.length() == 2
    store.delete(first)
    transaction.commit()
    assert store.length() == 1

    store.clear()
    transaction.commit()
    assert store.length() == 0
    assert other.length() == 1  # anderes Objekt unberührt
