# Try-out stack

A ready-to-click local setup: Plone 6.2 backend (official container, packages
installed from Test PyPI at start), PostgreSQL, and a Volto frontend with the
form block.

## Backend + database (docker)

    make backend

Starts PostgreSQL (host port 5433), runs the schema migration once, and boots
Plone on <http://localhost:8080> with a Volto-ready site `Plone` (admin/admin)
and both add-ons installed.

## Frontend (local pnpm, one-time install ~5 min)

    make frontend-install   # clones Volto 19.4.1 + installs deps
    make frontend           # dev server on http://localhost:3000

## Click through

1. <http://localhost:3000> → log in (admin/admin).
2. Add a page → add a **Form** block. In the block sidebar:
   - fill **Recipients** and **Mail subject** (required by the block even for
     store-only forms),
   - pick **Captcha provider: Honeypot Support** (volto-form-block treats a
     captcha as required config; the stack ships the invisible honeypot via
     `HONEYPOT_FIELD` + the `[honeypot]` extra),
   - enable **Store compiled data**,
   - disable **Send email to recipient** (no mail host in this stack).
   The form stays hidden in view mode until this config is complete.
3. Save → publish the page (anonymous submits need a published page).
4. Open the page (private window for an anonymous submit) → fill → submit →
   "Sent!".
5. Data in SQL (`author` is the login, NULL for anonymous):

       psql postgresql://formstore:formstore@localhost:5433/formstore \
         -c 'TABLE formstore_entry;'

`make clean` resets everything including the database.

## Notes

- The frontend is a pnpm workspace around a Volto 19.4.1 core checkout
  (mrs-developer). `pnpm-workspace.yaml` carries the catalog generated from
  `core/catalog.json`, and `package.json` mirrors Volto's root pnpm settings
  (patchedDependencies etc.) — both are pinned to the core tag.
- `packages/formstore-demo-policy` re-registers the `reactDnd` lazy libs that
  Volto 19 removed but volto-subblocks still needs.
