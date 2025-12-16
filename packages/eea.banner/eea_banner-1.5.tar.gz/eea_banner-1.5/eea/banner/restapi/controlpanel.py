"""Banner Controlpanel API"""

from zope.interface import Interface
from zope.component import adapter
from plone.restapi.controlpanels import RegistryConfigletPanel
from eea.banner.interfaces import IBannerSettings
from eea.banner.interfaces import IEeaBannerLayer


@adapter(Interface, IEeaBannerLayer)
class BannerControlpanel(RegistryConfigletPanel):
    """Banner Control Panel"""

    schema = IBannerSettings
    schema_prefix = None
    configlet_id = "banner"
    configlet_category_id = "Products"
    title = "Banner Settings"
    group = "Products"
