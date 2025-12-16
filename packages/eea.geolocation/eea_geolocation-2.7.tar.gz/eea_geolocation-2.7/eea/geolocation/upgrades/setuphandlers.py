"""Custom setup"""

from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):
    """Hidden profiles"""

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "eea.geolocation:uninstall",
            "eea.geolocation.upgrades:2",
        ]
