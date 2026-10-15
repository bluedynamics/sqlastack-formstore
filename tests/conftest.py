"""Shared test fixtures for sqlastack-formstore."""

from __future__ import annotations

from sqlastack.plone import reset_registry
import pytest
import sqlastack.formstore.models  # noqa: F401  (populate SQLModel.metadata)
import transaction


pytest_plugins = ["sqlastack.core.testing"]


@pytest.fixture
def forms_env(pg_url, pg_engine, monkeypatch):
    monkeypatch.setenv("SQLASTACK_FORMS_URL", pg_url)
    reset_registry()
    yield
    transaction.abort()
    reset_registry()
