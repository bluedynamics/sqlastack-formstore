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
2. Add a page → add a **Form** block → add some fields → in the block sidebar
   enable **Store compiled data**  → publish the page.
3. Open the page (or a private window for an anonymous submit) → fill →
   submit.
4. Data: block sidebar shows the stored records (CSV export, clear) — and in
   SQL: `psql postgresql://formstore:formstore@localhost:5433/formstore -c
   'TABLE formstore_entry;'`

`make clean` resets everything including the database.
