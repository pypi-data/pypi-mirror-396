"""Control Panel"""

from plone.app.registry.browser import controlpanel
from eea.zotero.interfaces import IZoteroClientSettings
from eea.zotero import EEAMessageFactory as _


class ZoteroControlPanelForm(controlpanel.RegistryEditForm):
    """RabbitMQClientControlPanelForm."""

    id = "zotero"
    label = _("Zotero Settings")
    schema = IZoteroClientSettings


class ZoteroControlPanelView(controlpanel.ControlPanelFormWrapper):
    """Zotero Control Panel"""

    form = ZoteroControlPanelForm
