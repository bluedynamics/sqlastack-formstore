"""IFormDataStore adapter storing submissions in SQL (JSONB).

This module imports NOTHING from collective.volto.formsupport or Plone: the
adapter's ``provides``/``for`` are declared purely in configure.zcml, so the
package stays importable (and testable) without the Plone stack. The de-facto
store contract (add/search/length/delete/clear; records with ``.attrs`` and
``.intid``) was verified against formsupport source on 2026-09-18 (spec §3).
"""

from __future__ import annotations

from sqlastack.formstore.models import FormEntry
from sqlastack.formstore.repository import FormEntryRepository
from sqlastack.plone import get_registry
import copy
import json
import logging


logger = logging.getLogger(__name__)

FORMS_DB_NAME = "forms"


def _flat_blocks(context) -> dict:
    """Port of formsupport's get_blocks: all blocks incl. nested containers."""
    blocks = copy.deepcopy(getattr(context, "blocks", {}) or {})
    if isinstance(blocks, str):
        blocks = json.loads(blocks)
    flat: dict = {}
    queue = list(blocks.items())
    while queue:
        block_id, block = queue.pop()
        flat[block_id] = block
        data = block.get("data")
        if isinstance(data, dict) and "blocks" in data:
            queue.extend(data["blocks"].items())
        if "blocks" in block:
            queue.extend(block["blocks"].items())
    return flat


class SQLRecord:
    """souper-Record duck type: ``.attrs`` mapping + ``.intid``.

    ``attrs["date"]`` is NAIVE local time on purpose: formsupport's expiry
    check compares it against ``datetime.now()`` (spec §3).
    """

    __slots__ = ("attrs", "intid")

    def __init__(self, entry: FormEntry) -> None:
        attrs = dict(entry.data)
        attrs["fields_labels"] = dict(entry.fields_labels)
        attrs["fields_order"] = list(entry.fields_order)
        attrs["fields_types"] = dict(entry.fields_types)
        attrs["block_id"] = entry.block_id
        attrs["date"] = entry.created_at.astimezone().replace(tzinfo=None)
        self.attrs = attrs
        self.intid = entry.id


class SQLFormDataStore:
    """Store form submissions in the ``forms`` database.

    Sessions come from the process-wide registry's shared Zope session; the
    Zope transaction manager commits/aborts — this adapter never commits.
    """

    def __init__(self, context, request) -> None:
        self.context = context
        self.request = request

    # -- plumbing ---------------------------------------------------------

    def _session(self):
        return get_registry().zope_session(FORMS_DB_NAME)

    def _repository(self) -> FormEntryRepository:
        return FormEntryRepository(self._session())

    def _request_data(self) -> dict:
        raw = self.request.get("BODY") if hasattr(self.request, "get") else None
        if raw:
            try:
                result = json.loads(raw)
            except (TypeError, ValueError):
                pass
            else:
                if isinstance(result, dict):
                    return result
        return dict(getattr(self.request, "form", None) or {})

    @property
    def block_id(self) -> str:
        return self._request_data().get("block_id", "")

    def _form_fields(self) -> list[dict]:
        block = _flat_blocks(self.context).get(self.block_id) or {}
        if block.get("@type") != "form":
            return []
        form_block = copy.deepcopy(block)
        subblocks = form_block.get("subblocks", [])
        for index, field in enumerate(subblocks):
            custom = form_block.get(field.get("field_id", ""))
            if custom:
                subblocks[index]["custom_field_id"] = custom
        return subblocks

    def _current_userid(self) -> str | None:
        """Login of the authenticated user; None = anonymous.

        AccessControl is only available inside a Zope process — outside
        (tests, tooling) every submission counts as anonymous.
        """
        try:
            from AccessControl import getSecurityManager
        except ImportError:
            return None
        user = getSecurityManager().getUser()
        if user is None:
            return None
        userid = user.getUserName()
        if not userid or userid == "Anonymous User":
            return None
        return userid

    # -- store contract (spec §3) -----------------------------------------

    def add(self, data) -> int | None:
        form_fields = self._form_fields()
        if not form_fields:
            logger.error(
                "Block %r of type 'form' not found on %s",
                self.block_id,
                self.context.absolute_url(),
            )
            return None
        fields = {
            f["field_id"]: {
                "label": f.get("custom_field_id", f.get("label", f["field_id"])),
                "type": f.get("field_type", "text"),
            }
            for f in form_fields
        }
        payload: dict = {}
        labels: dict = {}
        types: dict = {}
        order: list[str] = []
        for field_data in data:
            field_id = field_data.get("field_id", "")
            if field_id not in fields:
                continue
            field = fields[field_id]
            if field["type"] == "attachment":
                logger.warning(
                    "Skipping attachment field %r: file attachments are not "
                    "stored by sqlastack.formstore (yet)",
                    field_id,
                )
                continue
            payload[field_id] = field_data.get("value", "")
            labels[field_id] = field["label"]
            types[field_id] = field["type"]
            order.append(field_id)
        entry = self._repository().create(
            FormEntry(
                plone_uid=self.context.UID(),
                block_id=self.block_id,
                author=self._current_userid(),
                data=payload,
                fields_labels=labels,
                fields_types=types,
                fields_order=order,
            )
        )
        return entry.id

    def search(self, query=None) -> list[SQLRecord]:
        entries = self._repository().list_for(self.context.UID())
        return [SQLRecord(entry) for entry in entries]

    def length(self) -> int:
        return self._repository().count_for(self.context.UID())

    def delete(self, id) -> None:
        self._repository().delete_for(self.context.UID(), int(id))

    def clear(self) -> None:
        self._repository().clear_for(self.context.UID())
