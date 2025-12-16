"""Relations"""

from zope.component import getAdapter
from eea.api.versions.relations.interfaces import IGroupRelations
from Products.Five import BrowserView


class EEAVersionsView(BrowserView):
    """Default report view"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.context = context
        self.request = request

    def get_simple_version_info(self, brains):
        """return simple brain info needed for restapi"""
        res = []
        for brain in brains:
            res.append(
                {
                    "@id": brain.getURL(1),
                    "title": brain.Title,
                    "type": brain.portal_type,
                    "review_state": brain.review_state,
                    "effective": brain.EffectiveDate,
                }
            )
        return res

    def newer_versions(self):
        """returns newer versions if any"""
        relations = getAdapter(self.context, IGroupRelations)
        brains = relations.forward()
        return self.get_simple_version_info(brains)

    def older_versions(self):
        """return older versions if any"""
        relations = getAdapter(self.context, IGroupRelations)
        brains = relations.backward()
        return self.get_simple_version_info(brains)
