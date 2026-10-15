"""Shared block/payload shapes for the plone.formblock e2e tests."""

from __future__ import annotations


FORM_BLOCKS = {
    "text-1": {"@type": "text"},
    "form-id": {
        "@type": "schemaForm",
        "store": True,
        "send": False,
        "subject": "test subject",
        "schema": {
            "fieldsets": [
                {
                    "id": "default",
                    "title": "Default",
                    "fields": ["message", "name", "cv"],
                },
            ],
            "properties": {
                "message": {"title": "Message"},
                "name": {"title": "Name"},
                "cv": {"title": "CV", "type": "object", "factory": "File Upload"},
            },
            "required": [],
        },
    },
}

SUBMIT_PAYLOAD = {
    "block_id": "form-id",
    "data": {
        "message": "just want to say hi",
        "name": "John",
        "cv": {
            "data": "ZmFrZSBwZGY=",
            "encoding": "base64",
            "content-type": "application/pdf",
            "filename": "cv.pdf",
        },
        "sneaky": "not in schema",
    },
}
