# sqlastack-formstore

Store [collective.volto.formsupport](https://github.com/collective/collective.volto.formsupport)
form submissions in PostgreSQL instead of the default soup/annotation storage:
form data as JSONB, metadata (content UID, block id, author, timestamps) as
columns. Listing, CSV export, clearing and the retention mechanism of
formsupport keep working unchanged.

Part of the sqlastack family (built on
[sqlastack-core](https://github.com/bluedynamics/sqlastack-core)).

## How it works

- An `IFormDataStore` adapter (`sqlastack.formstore.store.SQLFormDataStore`)
  is registered for `(IDexterityContent, ISqlastackFormstoreLayer)` — install
  the GenericSetup profile and it wins over the default store, no
  overrides.zcml needed.
- Sessions come from a process-wide `sqlastack` database registry; writes join
  the Zope transaction (commit/abort by the publisher). Request-end teardown
  is wired via `IPubSuccess`/`IPubFailure` subscribers.
- The Python code imports nothing from formsupport or Plone — the adapter
  contract is declared purely in ZCML.

## Installation

1. Add `sqlastack-formstore` to your Plone deployment (Plone 6 / Volto with
   collective.volto.formsupport; contract verified against formsupport
   3.3.2, source-verified 2026-09-18).
2. Configure the database connection in the Zope process environment:

       SQLASTACK_FORMS_URL=postgresql+psycopg://user:pass@host/dbname

   (Optional pool tuning: `SQLASTACK_FORMS_POOL_SIZE` etc.)
3. Create the schema: `alembic upgrade head` (run from this package, uses the
   same `SQLASTACK_FORMS_URL`).
4. Install the **sqlastack.formstore** profile (Site Setup → Add-ons).
5. Enable *Store* on your form block — submissions now land in SQL.

## Limitations

- File attachment fields are not persisted (skipped with a log warning);
  attachment e-mailing by formsupport is unaffected.
- PostgreSQL only.

## Development

    uv sync --extra develop
    uv run pytest    # needs Docker (testcontainers, postgres:16)

License: GPL-2.0-only
