"""End-to-end: formsupport's listing/CSV/clear endpoints on top of the SQL store."""

from __future__ import annotations

from testdata import SUBMIT_PAYLOAD
import csv
import io


def _submit(session, url, payload=SUBMIT_PAYLOAD):
    response = session.post(f"{url}/@submit-form", json=payload)
    assert response.status_code == 200, response.text


def test_form_data_listing(form_document, anon_session, manager_session):
    url, uid = form_document
    _submit(anon_session, url)

    response = manager_session.get(f"{url}/@form-data")
    assert response.status_code == 200
    data = response.json()
    assert data["items_total"] == 1
    item = data["items"][0]
    assert item["message"]["value"] == "just want to say hi"
    assert item["message"]["label"] == "Message"
    # expand_records wickelt auch block_id als Feld-Dict ein (Upstream-Verhalten)
    assert item["block_id"]["value"] == "form-id"
    assert item["id"]  # intid = SQL-PK
    # ohne remove_data_after_days liefert formsupport None (expire_date and ...)
    assert not item["__expired"]


def test_form_data_listing_needs_permission(form_document, anon_session):
    url, uid = form_document
    _submit(anon_session, url)
    response = anon_session.get(f"{url}/@form-data")
    assert response.status_code in (401, 403)


def test_csv_export(form_document, anon_session, manager_session):
    url, uid = form_document
    _submit(anon_session, url)

    response = manager_session.get(f"{url}/@form-data-export")
    assert response.status_code == 200
    rows = list(csv.reader(io.StringIO(response.text)))
    header, first = rows[0], rows[1]
    assert "Message" in header
    assert "Name" in header
    message_idx = header.index("Message")
    assert first[message_idx] == "just want to say hi"


def test_clear_removes_only_this_documents_data(
    functional, form_document, anon_session, manager_session, form_entries
):
    from plone import api
    from plone.app.testing import TEST_USER_ID
    from plone.app.testing import setRoles
    from testdata import FORM_BLOCKS
    import transaction

    url, uid = form_document
    _submit(anon_session, url)

    # zweites Dokument mit eigenem Eintrag
    portal = functional["portal"]
    setRoles(portal, TEST_USER_ID, ["Manager"])
    other = api.content.create(type="Document", title="Other form", container=portal)
    other.blocks = dict(FORM_BLOCKS)
    api.content.transition(obj=other, transition="publish")
    transaction.commit()
    _submit(anon_session, other.absolute_url())
    assert len(form_entries()) == 2

    response = manager_session.delete(f"{url}/@form-data-clear")
    assert response.status_code == 204

    remaining = form_entries()
    assert len(remaining) == 1
    assert remaining[0]["plone_uid"] == other.UID()  # nur das andere Dokument bleibt
