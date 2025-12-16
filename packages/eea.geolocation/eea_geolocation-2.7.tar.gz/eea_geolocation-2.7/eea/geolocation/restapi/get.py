"""RestAPI enpoint @geolocation GET"""

from collective.taxonomy.interfaces import ITaxonomy
from eea.geolocation.interfaces import IGeolocationClientSettings
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.restapi.services import Service
from zope.component import getUtility, queryUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class Get(Service):
    """GET"""

    def reply(self):
        """Reply"""
        return {
            "google": {
                "password": api.portal.get_registry_record(
                    "maps_api_key", interface=IGeolocationClientSettings, default=""
                ),
            },
            "geonames": {
                "password": api.portal.get_registry_record(
                    "geonames_key", interface=IGeolocationClientSettings, default=""
                ),
            },
        }


class GetVocabularies(Service):
    """GetVocabularies"""

    def reply(self):
        """Reply"""
        normalizer = getUtility(IIDNormalizer)
        geodata = {}
        biodata = {}
        countrydata = {}
        data = {}

        # Geotags
        name = "eea.geolocation.geotags.taxonomy"
        identifier = "placeholderidentifier"

        normalized_name = normalizer.normalize(name).replace("-", "")
        utility_name = "collective.taxonomy." + normalized_name
        taxonomy = queryUtility(ITaxonomy, name=utility_name)

        try:
            vocabulary = taxonomy(self)
        except:
            vocabulary = taxonomy.makeVocabulary("en")

        for value, key in vocabulary.iterEntries():
            value = value.encode("latin-1", "ignore").decode("latin-1")

            if identifier not in value:
                identifier = value
                data = {}
                data.update({"title": identifier})
                identifier_key = "_".join(value.split(" ")).lower()
                geodata.update({identifier_key: data})

            if "geo" not in value:
                country = value.split(identifier)[-1]
            else:
                geo = value.split(country)[-1]
                data.update({geo: country})

        # Biotags
        name = "eea.geolocation.biotags.taxonomy"
        identifier = "placeholderidentifier"
        normalized_name = normalizer.normalize(name).replace("-", "")
        utility_name = "collective.taxonomy." + normalized_name
        taxonomy = queryUtility(ITaxonomy, name=utility_name)

        try:
            vocabulary = taxonomy(self)
        except:
            vocabulary = taxonomy.makeVocabulary("en")

        data = {}
        for value, key in vocabulary.iterEntries():
            value = value.encode("latin-1", "ignore").decode("latin-1")

            if identifier not in value:
                identifier = value
                data = {}
                data.update({"title": identifier})

            if "latitude" in value:
                latitude = value.split("latitude")[-1]
                data.update({"latitude": latitude})

            if "longitude" in value:
                longitude = value.split("longitude")[-1]
                data.update({"longitude": longitude})

            if "Abbreviation" in value:
                identifier_key = value.split("Abbreviation")[-1]
                biodata.update({identifier_key: data})
        del biodata[""]

        # Country mappings
        name = "eea.geolocation.countries_mapping.taxonomy"
        identifier = "placeholderidentifier"
        normalized_name = normalizer.normalize(name).replace("-", "")
        utility_name = "collective.taxonomy." + normalized_name
        taxonomy = queryUtility(ITaxonomy, name=utility_name)

        try:
            vocabulary = taxonomy(self)
        except:
            vocabulary = taxonomy.makeVocabulary("en")

        for value, key in vocabulary.iterEntries():
            value = value.encode("latin-1", "ignore").decode("latin-1")

            if identifier not in value:
                identifier = value
            else:
                country = value.split(identifier)[-1]
                if country == "":
                    country = identifier
                countrydata.update({country: identifier})

        return {
            "geotags": geodata,
            "biotags": biodata,
            "country_mappings": countrydata,
        }
