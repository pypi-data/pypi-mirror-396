"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from zope import schema
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from eea.geolocation import EEAMessageFactory as _


class IEeaGeolocationLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IGeolocationClientSettings(Interface):
    """Client settings for Geolocation"""

    maps_api_key = schema.TextLine(
        title=_("Google Maps API key"),
        description=_(
            "This will be used to render the Google Maps widget "
            "for eea.geotags enabled location fields. "
            "You can get one from "
            "https://developers.google.com/maps/documentation/javascript/"
            "get-api-key "
            "Leave empty to use Open Street Map instead"
        ),
        required=False,
        default="",
    )

    geonames_key = schema.TextLine(
        title=_("Geonames key"),
        description=_("http://www.geonames.org/"),
        required=False,
        default="",
    )
