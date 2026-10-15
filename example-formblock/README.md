# Try-out stack (plone.formblock)

A ready-to-click local setup for the **plone.formblock** stack: Plone 6.2
backend (official container, sqlastack-formstore from Test PyPI,
plone.formblock from PyPI), PostgreSQL, and a Volto 19 frontend with
`@plone/volto-form-block`.

Ports are offset from `../example/` (db **5434**, backend **8081**) so both
try-out stacks can run side by side; the frontends share port 3000, so start
only one at a time.

## Backend + database (docker)

    make backend

Starts PostgreSQL (host port 5434), runs the schema migration once, and boots
Plone on <http://localhost:8081> with a Volto-ready site `Plone` (admin/admin)
and both add-ons installed.

## Frontend (local pnpm, one-time install ~5 min)

    make frontend-install   # clones Volto 19.4.1 + installs deps
    make frontend           # dev server on http://localhost:3000

## Click through

0. One-time: set a site e-mail sender (Site Setup → Mail → sender address +
   name, anything like `demo@example.org` works). plone.formblock 1.0.0a3
   crashes on submit without one — even with sending disabled.
1. <http://localhost:3000> → log in (admin/admin).
2. Add a page → add a **Form** block and define some fields. In the block
   sidebar:
   - enable **Store compiled data**,
   - disable sending e-mail (no mail host in this stack),
   - a captcha is optional with plone.formblock — none needed here.
3. Save → publish the page (anonymous submits need a published page).
4. Open the page (private window for an anonymous submit) → fill → submit.
5. Data in SQL (`author` is the login, NULL for anonymous):

       psql postgresql://formstore:formstore@localhost:5434/formstore \
         -c 'TABLE formstore_entry;'

`make clean` resets everything including the database.

## Notes

- The frontend is a pnpm workspace around a Volto 19.4.1 core checkout
  (mrs-developer). `pnpm-workspace.yaml` carries the catalog generated from
  `core/catalog.json`, and `package.json` mirrors Volto's root pnpm settings
  (patchedDependencies etc.) — both are pinned to the core tag.
- Unlike the formsupport demo, no extra addons are needed:
  `@plone/volto-form-block` is built for Volto 19 (no volto-subblocks, no
  reactDnd shim, no forced captcha provider).
