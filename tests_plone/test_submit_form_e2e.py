"""End-to-end: Volto form submit through the real Plone publisher into SQL."""

from __future__ import annotations

from testdata import SUBMIT_PAYLOAD


def test_anonymous_submit_persists_row(form_document, anon_session, form_entries):
    url, uid = form_document
    response = anon_session.post(f"{url}/@submit-form", json=SUBMIT_PAYLOAD)
    assert response.status_code == 200, response.text

    rows = form_entries()
    assert len(rows) == 1
    row = rows[0]
    assert row["plone_uid"] == uid
    assert row["block_id"] == "form-id"
    assert row["author"] is None  # anonym
    assert row["data"] == {
        "message": "just want to say hi",
        "name": "John",
    }  # NUR Feldwerte: sneaky (nicht im Schema) und cv (Attachment) fehlen
    assert row["fields_labels"] == {"message": "Message", "name": "Name"}
    assert row["fields_order"] == ["message", "name"]


def test_authenticated_submit_records_author(
    form_document, manager_session, form_entries
):
    from plone.app.testing import SITE_OWNER_NAME

    url, uid = form_document
    response = manager_session.post(f"{url}/@submit-form", json=SUBMIT_PAYLOAD)
    assert response.status_code == 200, response.text

    rows = form_entries()
    assert len(rows) == 1
    assert rows[0]["author"] == SITE_OWNER_NAME  # echter AccessControl-Pfad


def test_unknown_block_stores_nothing(form_document, anon_session, form_entries):
    url, uid = form_document
    payload = dict(SUBMIT_PAYLOAD, block_id="missing")
    response = anon_session.post(f"{url}/@submit-form", json=payload)
    assert response.status_code == 400
    assert form_entries() == []
