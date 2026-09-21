"""Layer boots: ZCML loaded, profile installed, adapter beats the soup store."""

from __future__ import annotations


def test_profile_installed_browserlayer_active(functional):
    from plone.browserlayer.utils import registered_layers
    from sqlastack.formstore.interfaces import ISqlastackFormstoreLayer

    assert ISqlastackFormstoreLayer in registered_layers()


def test_request_end_subscribers_registered(functional):
    from sqlastack.plone import close_zope_sessions
    from zope.component import getGlobalSiteManager
    from ZPublisher.interfaces import IPubFailure
    from ZPublisher.interfaces import IPubSuccess

    gsm = getGlobalSiteManager()
    for iface in (IPubSuccess, IPubFailure):
        handlers = list(gsm.adapters.subscriptions((iface,), None))
        assert close_zope_sessions in handlers, iface


def test_adapter_overrides_soup_store(functional):
    from collective.volto.formsupport.interfaces import IFormDataStore
    from plone import api
    from plone.app.testing import TEST_USER_ID
    from plone.app.testing import setRoles
    from sqlastack.formstore.interfaces import ISqlastackFormstoreLayer
    from sqlastack.formstore.store import SQLFormDataStore
    from zope.component import getMultiAdapter
    from zope.interface import alsoProvides

    portal = functional["portal"]
    request = functional["request"]
    setRoles(portal, TEST_USER_ID, ["Manager"])
    doc = api.content.create(type="Document", title="Doc", container=portal)
    alsoProvides(request, ISqlastackFormstoreLayer)

    store = getMultiAdapter((doc, request), IFormDataStore)
    assert isinstance(store, SQLFormDataStore)
