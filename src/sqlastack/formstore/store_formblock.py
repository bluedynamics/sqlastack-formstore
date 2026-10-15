"""IFormDataStore adapter for plone.formblock's ``schemaForm`` blocks.

Like ``store``, this module imports nothing from plone.formblock: the
adapter's ``provides``/``for`` are declared purely in configure.zcml. The
de-facto contract differences to formsupport (records arrive as
``{"field_id", "value", "label"}`` dicts, fields are defined in the block's
JSON schema, ``fields_types`` must stay out of record attrs) were verified
against plone.formblock 1.0.0a3 source on 2026-10-15.
"""

from __future__ import annotations

from sqlastack.formstore.store import SQLFormDataStoreBase


class FormBlockDataStore(SQLFormDataStoreBase):
    """Adapter for plone.formblock's ``schemaForm`` blocks."""

    block_type = "schemaForm"
    # formblock's expand_records only skips fields_labels/fields_order —
    # fields_types in attrs would be rendered as a form field.
    record_includes_types = False

    def _field_specs(self) -> dict[str, dict]:
        block = self._block()
        properties = (block.get("schema") or {}).get("properties") or {}
        specs: dict[str, dict] = {}
        for field_id, field in properties.items():
            specs[field_id] = {
                "label": field.get("title", field_id),
                # the factory name is more telling than the JSON-schema type
                "type": field.get("factory") or field.get("type") or "",
                # upstream skips type "object" in get_records and collects
                # factory "File Upload" as attachments — treat both as files
                "attachment": (
                    field.get("type") == "object"
                    or field.get("factory") == "File Upload"
                ),
            }
        return specs
