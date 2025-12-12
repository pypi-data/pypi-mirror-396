from ftw.upgrade import UpgradeStep


class AddTheDSEToolSpecificPortalTypesInTheNavigation(UpgradeStep):
    """Add the DS eTool specific portal types in the navigation."""

    def __call__(self):
        self.install_upgrade_profile()
