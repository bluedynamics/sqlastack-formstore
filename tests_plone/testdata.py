"""Shared block/payload test data for the Plone integration tests.

In its own module (not conftest.py): when tests/ and tests_plone/ run in one
pytest invocation, the module name ``conftest`` resolves to whichever conftest
loaded first — importing from it would break the combined run.
"""

from __future__ import annotations


FORM_BLOCKS = {
    "text-id": {"@type": "text"},
    "form-id": {
        "@type": "form",
        "store": True,
        "subblocks": [
            {"label": "Message", "field_id": "message", "field_type": "text"},
            {"label": "Name", "field_id": "name", "field_type": "text"},
            {"label": "CV", "field_id": "cv", "field_type": "attachment"},
        ],
    },
}

SUBMIT_PAYLOAD = {
    "from": "john@doe.com",
    "subject": "test subject",
    "block_id": "form-id",
    "data": [
        {"field_id": "message", "value": "just want to say hi"},
        {"field_id": "name", "value": "John"},
        {"field_id": "sneaky", "value": "skip this"},
    ],
}
