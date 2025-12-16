"""Control panel module"""

from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm

from eea.banner.interfaces import IBannerSettings


class BannerRegistryEditForm(RegistryEditForm):
    """Banner Registry Edit Form"""

    schema = IBannerSettings
    id = "banner"
    label = "Banner Settings"


class BannerControlPanelFormWrapper(ControlPanelFormWrapper):
    """Banner Control Panel Form Wrapper"""

    form = BannerRegistryEditForm
