"""End-to-end: Volto form submit through the real Plone publisher into SQL."""

from __future__ import annotations

from testdata import SUBMIT_PAYLOAD


def test_anonymous_submit_persists_row(form_document, anon_session, form_entries):
    url, uid = form_document
    response = anon_session.post(f"{url}/@submit-form", json=SUBMIT_PAYLOAD)
    assert response.status_code == 200, response.text

    rows = form_entries()
    assert len(rows) == 1
    plone_uid, block_id, author, data = rows[0]
    assert plone_uid == uid
    assert block_id == "form-id"
    assert author is None  # anonym
    assert data["message"] == "just want to say hi"
    assert data["name"] == "John"
    assert "sneaky" not in data  # nicht im Schema
    assert "cv" not in data  # Attachment übersprungen
    assert data["fields_labels"] == {"message": "Message", "name": "Name"}
    assert data["fields_order"] == ["message", "name"]


def test_authenticated_submit_records_author(
    form_document, manager_session, form_entries
):
    from plone.app.testing import SITE_OWNER_NAME

    url, uid = form_document
    response = manager_session.post(f"{url}/@submit-form", json=SUBMIT_PAYLOAD)
    assert response.status_code == 200, response.text

    rows = form_entries()
    assert len(rows) == 1
    assert rows[0][2] == SITE_OWNER_NAME  # author, echter AccessControl-Pfad


def test_unknown_block_stores_nothing(form_document, anon_session, form_entries):
    url, uid = form_document
    payload = dict(SUBMIT_PAYLOAD, block_id="missing")
    response = anon_session.post(f"{url}/@submit-form", json=payload)
    assert response.status_code == 400
    assert form_entries() == []
