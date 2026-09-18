"""Run this package's Alembic migrations against SQLASTACK_FORMS_URL.

Console script for pip-installed deployments, where no alembic.ini or
migrations directory exists on disk — the migration scripts ship inside
the package and are addressed via Alembic's package-path syntax.
"""

from __future__ import annotations

from alembic import command
from alembic.config import Config


def upgrade(revision: str = "head") -> None:
    config = Config()
    config.set_main_option("script_location", "sqlastack.formstore:migrations")
    command.upgrade(config, revision)


def main() -> None:
    upgrade()
