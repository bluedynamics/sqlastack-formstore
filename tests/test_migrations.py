"""Alembic migrations run against a dedicated database on the test container."""

from __future__ import annotations

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlastack.formstore.migrate import upgrade
from sqlmodel import SQLModel
import pytest


@pytest.fixture
def alembic_db_url(pg_url, monkeypatch):
    admin = create_engine(pg_url, isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text("DROP DATABASE IF EXISTS alembic_test"))
        conn.execute(text("CREATE DATABASE alembic_test"))
    admin.dispose()
    url = (
        make_url(pg_url)
        .set(database="alembic_test")
        .render_as_string(hide_password=False)
    )
    monkeypatch.setenv("SQLASTACK_FORMS_URL", url)
    return url


def _upgrade_head():
    upgrade()


def test_upgrade_head_creates_table_and_index(alembic_db_url):
    _upgrade_head()
    engine = create_engine(alembic_db_url)
    inspector = inspect(engine)
    assert "formstore_entry" in inspector.get_table_names()
    index_names = {ix["name"] for ix in inspector.get_indexes("formstore_entry")}
    assert "ix_formstore_entry_form" in index_names
    engine.dispose()


def test_migrations_in_sync_with_model(alembic_db_url):
    _upgrade_head()

    def include_object(obj, name, type_, reflected, compare_to):
        if type_ == "table":
            return name == "formstore_entry"
        return True

    engine = create_engine(alembic_db_url)
    with engine.connect() as conn:
        ctx = MigrationContext.configure(
            conn, opts={"include_object": include_object}
        )
        diffs = compare_metadata(ctx, SQLModel.metadata)
    engine.dispose()
    assert diffs == [], f"model and migrations diverged: {diffs}"
