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
def form_entries():
    """Return all stored FormEntry rows as plain tuples (standalone session)."""

    def _rows():
        from sqlastack.formstore.models import FormEntry
        from sqlastack.plone import get_registry
        from sqlmodel import select

        with get_registry().session_scope("forms") as session:
            entries = session.scalars(select(FormEntry)).all()
            return [
                (e.plone_uid, e.block_id, e.author, dict(e.data)) for e in entries
            ]

    return _rows
