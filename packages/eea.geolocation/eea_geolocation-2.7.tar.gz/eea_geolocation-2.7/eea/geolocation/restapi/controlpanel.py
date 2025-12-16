"""Controlpanel API"""

from zope.interface import Interface
from zope.component import adapter
from plone.restapi.controlpanels import RegistryConfigletPanel
from eea.geolocation.interfaces import IGeolocationClientSettings
from eea.geolocation.interfaces import IEeaGeolocationLayer


@adapter(Interface, IEeaGeolocationLayer)
class Controlpanel(RegistryConfigletPanel):
    """Geolocation Control Panel"""

    schema = IGeolocationClientSettings
    configlet_id = "geolocation"
    configlet_category_id = "Products"
    schema_prefix = None
