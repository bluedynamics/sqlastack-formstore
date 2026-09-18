"""Zope interfaces for sqlastack.formstore."""

from __future__ import annotations

from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ISqlastackFormstoreLayer(IDefaultBrowserLayer):
    """Browser layer: marks sites with the sqlastack.formstore profile installed.

    Makes the SQL store adapter more specific than formsupport's default
    soup-based store, so no overrides.zcml is needed.
    """
