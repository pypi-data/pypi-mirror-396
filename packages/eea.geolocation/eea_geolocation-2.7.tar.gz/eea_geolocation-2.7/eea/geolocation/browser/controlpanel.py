"""Control Panel"""

from plone.app.registry.browser import controlpanel
from eea.geolocation.interfaces import IGeolocationClientSettings
from eea.geolocation import EEAMessageFactory as _


class ControlPanelForm(controlpanel.RegistryEditForm):
    """Client Control Panel Form."""

    id = "geolocation"
    label = _("Geolocation Settings")
    schema = IGeolocationClientSettings


class ControlPanelView(controlpanel.ControlPanelFormWrapper):
    """Control Panel"""

    form = ControlPanelForm
