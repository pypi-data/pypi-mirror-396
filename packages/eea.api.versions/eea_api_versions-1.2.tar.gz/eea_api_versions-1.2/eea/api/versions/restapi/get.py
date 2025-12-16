"""RESTful API endpoint for EEA Versions.
This module provides the GET endpoint for retrieving version information
for Plone content items.
"""

from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service

from Products.CMFCore.interfaces import ISiteRoot

from zope.interface import Interface
from zope.interface import implementer
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class EEAVersions:
    """EEA Versions"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False, prefix="expand.eea."):
        result = {
            "eea.versions": {"@id": f"{self.context.absolute_url()}/@eea.versions"}
        }

        # avoid large queries on layout pages where context is site
        request = getRequest()
        # don't query when we add a new page and we use report_navigation
        is_site = ISiteRoot.providedBy(self.context)
        if is_site or "add?type" in request.get("HTTP_REFERER", ""):
            return result

        relations = queryMultiAdapter((self.context, self.request), name="eea_versions")

        res = {
            "newer_versions": {
                "@id": f"{self.context.absolute_url()}/@newer-versions",
                "items": relations.newer_versions() if relations else [],
            },
            "older_versions": {
                "@id": f"{self.context.absolute_url()}/@older-versions",
                "items": relations.older_versions() if relations else [],
            },
        }
        result["eea.versions"].update(res)
        return result


class EEAVersionsGet(Service):
    """EEA Versions Get"""

    def reply(self):
        """Reply with versions"""
        versions = EEAVersions(self.context, self.request)
        return versions(expand=True, prefix="expand.eea.")["eea.versions"]
