"""plone.app.testing layers for sqlastack.formstore on plone.formblock.

Importable only with the ``test-plone-formblock`` extra installed — shipped
so downstream projects can stack their own layers on top. Kept separate from
``testing`` (the formsupport layers) so each extra only needs its own form
stack.
"""

from __future__ import annotations

from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.formblock.testing import FIXTURE as PLONE_FORMBLOCK_FIXTURE
from plone.testing.zope import WSGI_SERVER_FIXTURE


class SqlastackFormstoreFormblockLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FORMBLOCK_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import sqlastack.formstore

        self.loadZCML(package=sqlastack.formstore)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "sqlastack.formstore:default")


SQLASTACK_FORMSTORE_FORMBLOCK_FIXTURE = SqlastackFormstoreFormblockLayer()

SQLASTACK_FORMSTORE_FORMBLOCK_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(SQLASTACK_FORMSTORE_FORMBLOCK_FIXTURE, WSGI_SERVER_FIXTURE),
    name="SqlastackFormstoreFormblockLayer:Functional",
)
