"""Smoke: profile installed, browser layer active, our adapter wins."""

from __future__ import annotations


def test_profile_installed(functional):
    from plone import api

    portal = functional["portal"]
    installer = api.content.get_view("installer", portal, functional["request"])
    assert installer.is_product_installed("sqlastack.formstore")


def test_browserlayer_registered(functional):
    from plone.browserlayer.utils import registered_layers
    from sqlastack.formstore.interfaces import ISqlastackFormstoreLayer

    assert ISqlastackFormstoreLayer in registered_layers()


def test_our_adapter_overrides_soup_store(functional):
    from plone.formblock.interfaces import IFormDataStore
    from sqlastack.formstore.interfaces import ISqlastackFormstoreLayer
    from sqlastack.formstore.store_formblock import FormBlockDataStore
    from zope.component import getMultiAdapter
    from zope.interface import alsoProvides

    portal = functional["portal"]
    request = functional["request"]
    alsoProvides(request, ISqlastackFormstoreLayer)
    store = getMultiAdapter((portal, request), IFormDataStore)
    assert isinstance(store, FormBlockDataStore)
