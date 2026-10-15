# sqlastack-formstore

Store Volto form submissions in PostgreSQL instead of the default
soup/annotation storage: form data as JSONB, metadata (content UID, block id,
author, timestamps) as columns. Listing, CSV export, clearing and the
retention mechanism of the form packages keep working unchanged.

Both maintained Volto form stacks are supported, each via its own adapter on
the same table:

- [collective.volto.formsupport](https://github.com/collective/collective.volto.formsupport)
  (`form` blocks; contract verified against 3.3.2)
- [plone.formblock](https://github.com/plone/form-block) / `@plone/volto-form-block`
  (`schemaForm` blocks, Volto 19+; contract verified against 1.0.0a3)

Part of the sqlastack family (built on
[sqlastack-core](https://github.com/bluedynamics/sqlastack-core)).

## How it works

- `IFormDataStore` adapters (`sqlastack.formstore.store.SQLFormDataStore` for
  formsupport, `sqlastack.formstore.store_formblock.FormBlockDataStore` for
  plone.formblock) are registered for
  `(IDexterityContent, ISqlastackFormstoreLayer)` — install the GenericSetup
  profile and they win over the default stores, no overrides.zcml needed.
- Each adapter registration is guarded by a ZCML condition
  (`installed collective.volto.formsupport` / `installed plone.formblock`), so
  any subset of the two form packages may be present.
- Sessions come from a process-wide `sqlastack` database registry; writes join
  the Zope transaction (commit/abort by the publisher). Request-end teardown
  is wired via `IPubSuccess`/`IPubFailure` subscribers.
- The Python code imports nothing from the form packages or Plone — the
  adapter contracts are declared purely in ZCML.

## Installation

1. Add `sqlastack-formstore` to your Plone deployment, next to your form
   package (collective.volto.formsupport or plone.formblock). The adapters
   register only for form packages that are importable (ZCML condition), so
   the package is safe to install ahead of them.
2. Configure the database connection in the Zope process environment:

       SQLASTACK_FORMS_URL=postgresql+psycopg://user:pass@host/dbname

   (Optional pool tuning: `SQLASTACK_FORMS_POOL_SIZE` etc.)
3. Create the schema: run `sqlastack-formstore-migrate` (console script;
   uses the same `SQLASTACK_FORMS_URL`). From a source checkout, `alembic
   upgrade head` works too.
4. Install the **sqlastack.formstore** profile (Site Setup → Add-ons).
5. Enable *Store* on your form block — submissions now land in SQL.

## Limitations

- File attachment fields are not persisted (skipped with a log warning);
  attachment e-mailing by the form packages is unaffected.
- PostgreSQL only.

## Development

    uv sync --extra develop
    uv run pytest    # needs Docker (testcontainers, postgres:16)

### Plone integration tests

Real end-to-end tests (ZCML load, GS profile, adapter override, submit
endpoint through the actual publisher into PostgreSQL) live in `tests_plone/`
(formsupport, `@submit-form`) and `tests_plone_formblock/` (plone.formblock,
`@schemaform-data`). They are not part of the default test run — they boot a
full Plone site — and the two suites share file basenames, so run them in
separate pytest invocations (as CI does):

    uv sync --extra develop --extra test-plone
    uv run pytest tests_plone/              # slow: needs Docker + boots Plone

    uv sync --extra develop --extra test-plone-formblock
    uv run pytest tests_plone_formblock/

Requires a sibling checkout of sqlastack-core (path dependency via
`[tool.uv.sources]`).

License: GPL-2.0-only
