"""Custom setup"""

import os
from Products.CMFPlone.interfaces import INonInstallable
from zope.component import getUtility, queryUtility
from zope.interface import implementer
from zope.i18n.interfaces import ITranslationDomain
from zope.schema.interfaces import IVocabularyFactory
from plone.i18n.normalizer.interfaces import IIDNormalizer
from collective.taxonomy.exportimport import TaxonomyImportExportAdapter
from collective.taxonomy.factory import registerTaxonomy
from collective.taxonomy.interfaces import ITaxonomy

try:
    # Plone 4
    from Products.CMFPlone.interfaces import IFactoryTool

    assert IFactoryTool
    IS_PLONE_4 = True
except ImportError:
    IS_PLONE_4 = False


TAXONOMIES = {
    "eea.geolocation.biotags.taxonomy": "Biogeographical Regions",
    "eea.geolocation.geotags.taxonomy": "EEA Geolocation Geotags",
    "eea.geolocation.countries_mapping.taxonomy": "EEA Country Names Mappings",
}


@implementer(INonInstallable)
class HiddenProfiles(object):
    """Hidden profiles"""

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "eea.geolocation:uninstall",
        ]


def post_install(context):
    """Post install script"""
    site = context.aq_parent
    language = "en"
    if IS_PLONE_4:
        directory = "/profiles/plone4imports/"
    else:
        directory = "/profiles/plone5imports/"

    for name, title in TAXONOMIES.items():
        taxonomy = registerTaxonomy(site, name, title, language, "Created at install")
        path = os.path.dirname(os.path.realpath(__file__))
        path += directory + name + ".xml"

        with open(path) as xmlfile:
            data = xmlfile.read().encode()
            import_adapter = TaxonomyImportExportAdapter(site)
            import_adapter.importDocument(taxonomy, data)


def uninstall(context):
    """Uninstall script"""
    site = context.aq_parent
    normalizer = getUtility(IIDNormalizer)

    for name, title in TAXONOMIES.items():
        normalized_name = normalizer.normalize(name).replace("-", "")
        utility_name = "collective.taxonomy." + normalized_name
        taxonomy = queryUtility(ITaxonomy, name=utility_name)

        if IS_PLONE_4:
            from zope.component import getSiteManager

            sm = getSiteManager()
        else:
            sm = site.getSiteManager()

        sm.unregisterUtility(taxonomy, ITaxonomy, name=utility_name)
        sm.unregisterUtility(taxonomy, IVocabularyFactory, name=utility_name)
        sm.unregisterUtility(taxonomy, ITranslationDomain, name=utility_name)
