from ftw.upgrade import UpgradeStep
from plone import api
from Products.CMFPlone.WorkflowTool import WorkflowTool


class ChangeTheSectorsWorkflow(UpgradeStep):
    """Change the sectors workflow."""

    def __call__(self):
        self.install_upgrade_profile()
        pw: WorkflowTool = api.portal.get_tool("portal_workflow")
        pw.updateRoleMappings()
