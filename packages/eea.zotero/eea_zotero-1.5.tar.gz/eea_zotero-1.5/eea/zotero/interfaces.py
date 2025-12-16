"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from zope import schema
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from eea.zotero import EEAMessageFactory as _


class IEeaZoteroLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IZoteroClientSettings(Interface):
    """Client settings for Zotero"""

    server = schema.TextLine(
        title=_("Zotero API URL"),
        description=_("Zotero API URL including user/group id"),
        default="https://api.zotero.org/users/12345",
    )

    password = schema.TextLine(
        title=_("Zotero API KEY"),
        description=("Zotero API KEY with read/write permissions"),
        default="",
    )

    default = schema.TextLine(
        title=_("Zotero default collection"),
        description=("Zotero collection id where to store new citations"),
        default="",
    )

    style = schema.TextLine(
        title=_("Zotero citation style"),
        description=_("Zotero citation style, e.g.: oxford or an URL to a .csl file"),
        default="https://www.eea.europa.eu/zotero/eea.csl",
    )
