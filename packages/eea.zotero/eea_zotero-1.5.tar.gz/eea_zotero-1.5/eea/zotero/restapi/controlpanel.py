"""Zotero Controlpanel API"""

from zope.interface import Interface
from zope.component import adapter
from plone.restapi.controlpanels import RegistryConfigletPanel
from eea.zotero.interfaces import IZoteroClientSettings
from eea.zotero.interfaces import IEeaZoteroLayer


@adapter(Interface, IEeaZoteroLayer)
class ZoteroControlpanel(RegistryConfigletPanel):
    """Zotero Control Panel"""

    schema = IZoteroClientSettings
    configlet_id = "zotero"
    configlet_category_id = "Products"
    schema_prefix = None
