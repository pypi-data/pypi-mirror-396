from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "dsetool.policy:uninstall",
        ]

    def getNonInstallableProducts(self):
        return [
            "euphorie.deployment.upgrade",
            "euphorie.deployment",
            "euphorie.upgrade.content.v1",
            "euphorie.upgrade.deployment.v1",
            "euphorie.upgrade.deployment.v18",
            "ftw.upgrade",
            "osha.oira.upgrade.v1",
            "osha.oira.upgrade.v12",
            "osha.oira.upgrade",
            "osha.oira",
            "pas.plugins.ldap.plonecontrolpanel",
            "plone.app.caching",
            "plone.app.discussion",
            "plone.app.imagecropping",
            "plone.app.iterate",
            "plone.app.multilingual",
            "plone.formwidget.recaptcha",
            "plone.patternslib",
            "plone.restapi",
            "plone.session",
            "plone.volto",
            "plonetheme.nuplone",
            "Products.CMFPlacefulWorkflow",
            "Products.membrane",
            "yafowil.plone",
        ]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.


def _clean_up_plone_displayed_types():
    """Remove dsetool types from the plone.displayed_types registry record."""
    dsetool_types = {
        "euphorie.choice",
        "euphorie.recommendation",
        "euphorie.option",
    }
    displayed_types: tuple = api.portal.get_registry_record(
        "plone.displayed_types", default=()
    )
    new_displayed_types = tuple(
        type for type in displayed_types if type not in dsetool_types
    )
    if new_displayed_types != displayed_types:
        api.portal.set_registry_record("plone.displayed_types", new_displayed_types)


def post_uninstall(context):
    """Uninstall script"""
    _clean_up_plone_displayed_types()
