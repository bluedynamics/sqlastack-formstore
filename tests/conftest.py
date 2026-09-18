"""Shared test fixtures for sqlastack-formstore."""

from __future__ import annotations

import sqlastack.formstore.models  # noqa: F401  (populate SQLModel.metadata)


pytest_plugins = ["sqlastack.core.testing"]
