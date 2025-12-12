from Acquisition import aq_base
from ftw.upgrade import UpgradeStep
from Persistence.mapping import PersistentMapping
from plone import api
from Products.CMFPlone.WorkflowTool import WorkflowTool


class FixTheSecuritySettings(UpgradeStep):
    """Fix the security settings.
    _Access_contents_information_Permission
    _Modify_portal_content_Permission
    _View_Permission

    """

    def __call__(self):

        portal_types = [
            "euphorie.choice",
            "euphorie.recommendation",
            "euphorie.option",
        ]

        pw: WorkflowTool = api.portal.get_tool("portal_workflow")
        chains_by_type: PersistentMapping = pw._chains_by_type  # type: ignore

        for portal_type in portal_types:
            chains_by_type[portal_type] = ()

        permissions_attributes = [
            "_Access_contents_information_Permission",
            "_Modify_portal_content_Permission",
            "_View_Permission",
        ]

        brains = api.content.find(portal_type=portal_types)

        for brain in brains:
            obj = brain.getObject()
            obj_base = aq_base(obj)

            for permission in permissions_attributes:
                try:
                    delattr(obj_base, permission)
                except AttributeError:
                    pass

            obj.reindexObjectSecurity()
