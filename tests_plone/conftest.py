"""Fixtures for the Plone integration tests (real Plone + real PostgreSQL)."""

from __future__ import annotations

from pytest_plone import fixtures_factory
from sqlastack.formstore.testing import SQLASTACK_FORMSTORE_FUNCTIONAL_TESTING
import pytest
import sqlastack.formstore.models  # noqa: F401  (populate SQLModel.metadata)


pytest_plugins = ["sqlastack.core.testing"]

globals().update(
    fixtures_factory(((SQLASTACK_FORMSTORE_FUNCTIONAL_TESTING, "functional"),))
)


@pytest.fixture(autouse=True)
def forms_env(pg_url, pg_engine, monkeypatch):
    """Point the 'forms' database at the test container; fresh registry per test."""
    from sqlastack.plone import reset_registry

    monkeypatch.setenv("SQLASTACK_FORMS_URL", pg_url)
    reset_registry()
    yield
    reset_registry()


@pytest.fixture
def form_document(functional):
    from plone import api
    from plone.app.testing import TEST_USER_ID
    from plone.app.testing import setRoles
    from testdata import FORM_BLOCKS
    import transaction

    portal = functional["portal"]
    setRoles(portal, TEST_USER_ID, ["Manager"])
    doc = api.content.create(type="Document", title="Form page", container=portal)
    doc.blocks = dict(FORM_BLOCKS)
    # anonyme Submits brauchen View — Formularseiten sind real publiziert
    api.content.transition(obj=doc, transition="publish")
    transaction.commit()
    return doc.absolute_url(), doc.UID()


@pytest.fixture
def anon_session(functional):
    from plone.restapi.testing import RelativeSession

    portal_url = functional["portal"].absolute_url()
    session = RelativeSession(portal_url)
    session.headers.update({"Accept": "application/json"})
    yield session
    session.close()


@pytest.fixture
def manager_session(functional):
    from plone.app.testing import SITE_OWNER_NAME
    from plone.app.testing import SITE_OWNER_PASSWORD
    from plone.restapi.testing import RelativeSession

    portal_url = functional["portal"].absolute_url()
    session = RelativeSession(portal_url)
    session.headers.update({"Accept": "application/json"})
    session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
    yield session
    session.close()


@pytest.fixture
def form_entries():
    """Return all stored FormEntry rows as plain tuples (standalone session)."""

    def _rows():
        from sqlastack.formstore.models import FormEntry
        from sqlastack.plone import get_registry
        from sqlmodel import select

        with get_registry().session_scope("forms") as session:
            entries = session.scalars(select(FormEntry)).all()
            return [
                {
                    "plone_uid": e.plone_uid,
                    "block_id": e.block_id,
                    "author": e.author,
                    "data": dict(e.data),
                    "fields_labels": dict(e.fields_labels),
                    "fields_order": list(e.fields_order),
                    "fields_types": dict(e.fields_types),
                }
                for e in entries
            ]

    return _rows
