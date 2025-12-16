"""Reports relations interfaces"""

from zope.interface import Interface


class IGroupRelations(Interface):
    """Reports relations by group"""

    def backward():
        """Take all objects in the same group and return that that are older
        than this one.
        """

    def forward():
        """Take all objects in the same group and return that that are newer
        than this one.
        """
