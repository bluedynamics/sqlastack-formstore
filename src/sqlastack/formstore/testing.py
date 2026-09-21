"""plone.app.testing layers for sqlastack.formstore.

Importable only with the ``test-plone`` extra installed — this module is
shipped so downstream projects can stack their own layers on top.
"""

from __future__ import annotations

from collective.volto.formsupport.testing import VOLTO_FORMSUPPORT_API_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2


class SqlastackFormstoreLayer(PloneSandboxLayer):
    defaultBases = (VOLTO_FORMSUPPORT_API_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import sqlastack.formstore

        self.loadZCML(package=sqlastack.formstore)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "sqlastack.formstore:default")


SQLASTACK_FORMSTORE_FIXTURE = SqlastackFormstoreLayer()

SQLASTACK_FORMSTORE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SQLASTACK_FORMSTORE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="SqlastackFormstoreLayer:Functional",
)
