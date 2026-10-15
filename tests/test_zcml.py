"""Static sanity checks for ZCML and GS profile (no Plone needed)."""

from __future__ import annotations

from pathlib import Path
import importlib
import xml.etree.ElementTree as ET


PKG = Path(__file__).parents[1] / "src" / "sqlastack" / "formstore"


def test_zcml_and_profile_are_wellformed_xml():
    for path in (
        PKG / "configure.zcml",
        PKG / "profiles" / "default" / "browserlayer.xml",
        PKG / "profiles" / "default" / "metadata.xml",
    ):
        ET.parse(path)  # raises on malformed XML


def _resolve(dotted: str):
    module_name, attr = dotted.rsplit(".", 1)
    return getattr(importlib.import_module(module_name), attr)


def test_our_dotted_names_in_zcml_resolve():
    tree = ET.parse(PKG / "configure.zcml")
    ns = "{http://namespaces.zope.org/zope}"
    factories = [el.get("factory") for el in tree.iter(f"{ns}adapter")]
    handlers = [el.get("handler") for el in tree.iter(f"{ns}subscriber")]
    assert factories == [
        ".store.SQLFormDataStore",
        ".store_formblock.FormBlockDataStore",
    ]
    assert handlers == ["sqlastack.plone.close_zope_sessions"] * 2
    assert _resolve("sqlastack.formstore.store.SQLFormDataStore")
    assert _resolve("sqlastack.formstore.store_formblock.FormBlockDataStore")
    assert _resolve("sqlastack.plone.close_zope_sessions")
    assert _resolve("sqlastack.formstore.interfaces.ISqlastackFormstoreLayer")


def test_each_adapter_is_conditional_on_its_form_package():
    """Neither form stack is a hard dependency: every adapter registration
    must be guarded so the package loads with any subset installed."""
    tree = ET.parse(PKG / "configure.zcml")
    ns = "{http://namespaces.zope.org/zope}"
    zcml = "{http://namespaces.zope.org/zcml}"
    conditions = {
        el.get("factory"): el.get(f"{zcml}condition")
        for el in tree.iter(f"{ns}adapter")
    }
    assert conditions == {
        ".store.SQLFormDataStore": "installed collective.volto.formsupport",
        ".store_formblock.FormBlockDataStore": "installed plone.formblock",
    }
    provides = {
        el.get("factory"): el.get("provides") for el in tree.iter(f"{ns}adapter")
    }
    assert provides == {
        ".store.SQLFormDataStore": (
            "collective.volto.formsupport.interfaces.IFormDataStore"
        ),
        ".store_formblock.FormBlockDataStore": (
            "plone.formblock.interfaces.IFormDataStore"
        ),
    }


def test_browserlayer_points_to_our_interface():
    tree = ET.parse(PKG / "profiles" / "default" / "browserlayer.xml")
    layer = tree.getroot().find("layer")
    assert (
        layer.get("interface")
        == "sqlastack.formstore.interfaces.ISqlastackFormstoreLayer"
    )
