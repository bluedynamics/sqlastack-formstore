"""After real publisher requests, no SQL connection stays checked out.

The IPubSuccess/IPubFailure subscribers must have released every server
thread's zope session; a leak would show up as pool.checkedout() > 0.
"""

from __future__ import annotations

from testdata import SUBMIT_PAYLOAD
import time


def test_no_checked_out_connections_after_requests(
    form_document, anon_session, form_entries
):
    from sqlastack.plone import get_registry

    url, uid = form_document
    for _ in range(3):
        response = anon_session.post(f"{url}/@submit-form", json=SUBMIT_PAYLOAD)
        assert response.status_code == 200

    assert len(form_entries()) == 3

    pool = get_registry().session_factory("forms").engine.pool
    # der Server-Thread beendet die Publikation minimal nach der Response
    for _ in range(50):
        if pool.checkedout() == 0:
            break
        time.sleep(0.1)
    assert pool.checkedout() == 0
