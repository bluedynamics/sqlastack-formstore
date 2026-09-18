"""Shared test fixtures for sqlastack-formstore."""

from __future__ import annotations

import pytest
import sqlastack.formstore.models  # noqa: F401  (populate SQLModel.metadata)


pytest_plugins = ["sqlastack.core.testing"]


@pytest.fixture
def pg_registry(pg_engine):
    """DatabaseRegistry with non-expiring sessions for detached-object access."""
    from sqlalchemy.orm import sessionmaker

    from sqlastack.core.registry import DatabaseRegistry
    from sqlastack.core.session import SessionFactory

    registry = DatabaseRegistry()
    # Use expire_on_commit=False so test objects remain accessible after session close
    factory = SessionFactory(engine=pg_engine)
    factory._session_factory = sessionmaker(bind=pg_engine, expire_on_commit=False)
    registry.register_factory("fh", factory)
    yield registry
    # a test failing mid-zope-transaction must not bleed into the next test
    import transaction

    transaction.abort()
    registry.remove_zope_sessions()
