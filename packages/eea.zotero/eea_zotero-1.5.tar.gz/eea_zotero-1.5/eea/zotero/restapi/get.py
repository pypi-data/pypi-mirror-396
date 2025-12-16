"""RestAPI enpoint @zotero GET"""

from eea.zotero.interfaces import IZoteroClientSettings
from plone import api
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class ZoteroGet(Service):
    """Zotero GET"""

    def reply(self):
        """Reply"""
        return {
            "server": api.portal.get_registry_record(
                "server", interface=IZoteroClientSettings, default=""
            ),
            "password": api.portal.get_registry_record(
                "password", interface=IZoteroClientSettings, default=""
            ),
            "default": api.portal.get_registry_record(
                "default", interface=IZoteroClientSettings, default=""
            ),
            "style": api.portal.get_registry_record(
                "style", interface=IZoteroClientSettings, default=""
            ),
        }
