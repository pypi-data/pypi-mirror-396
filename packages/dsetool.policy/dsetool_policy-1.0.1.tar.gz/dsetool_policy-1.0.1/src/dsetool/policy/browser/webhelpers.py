from osha.oira.client.browser.webhelpers import OSHAWebHelpers
from plone import api
from plone.memoize.instance import memoize


class DSEToolWebHelpers(OSHAWebHelpers):
    """Browser view with utility methods that can be used in templates.
    View name: @@webhelpers
    """

    about_urls = {
        "en": "/dangerous-substances/about-e-tool.html",
        "no": "/dangerous-substances/no/om-e-verktøyet.html",
        "is": "/dangerous-substances/is/um-rafræna-tólið.html",
        "pt": "/dangerous-substances/pt/acerca-da-ferramenta-eletrónica.html",
        "sl": "/dangerous-substances/sl/o-e-orodju.html",
        "et": "/dangerous-substances/et/teave-e-vahendi-kohta.html",
        "de_AT": "/dangerous-substances/AT_de/über-das-e-tool.html",
        "ro": "/dangerous-substances/ro/despre-instrumentul-electronic.html",
        "de": "/dangerous-substances/de/über-das-e-tool.html",
        "es": "/dangerous-substances/es/acerca-de-la-herramienta-electrónica.html",
        "lt": "/dangerous-substances/lt/apie-epriemonę.html",
    }

    @property
    @memoize
    def custom_js(self):
        """Return custom JavaScript where necessary."""
        glossary_js = (
            f'<script src="{self.client_url}/++resource++dsetool.resources/'
            f'javascript/glossary.js" type="text/javascript"></script>'
        )
        return glossary_js

    @property
    @memoize
    def custom_css(self):
        """Return custom CSS where necessary."""
        styles_css = (
            f'<link href="{self.client_url}/++resource++dsetool.resources/'
            f'style/all.css" rel="stylesheet" type="text/css" />\n'
        )
        return styles_css + super().custom_css

    def get_about_url(self):
        """mapper of language to about url"""
        return self.about_urls.get(
            api.portal.get_current_language(), self.about_urls["en"]
        )
