"""RestAPI enpoint @banner GET"""

import os
import json
from contextlib import closing
from six.moves import urllib
from plone import api
from plone.restapi.services import Service
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

# from eea.cache import cache
from eea.banner.interfaces import IBannerSettings, IEeaBannerLayer

TIMEOUT = 15
RANCHER_METADATA = "http://rancher-metadata/latest"
MEMCACHE_AGE = 300


def isTrue(value):
    """Evaluate True"""
    if isinstance(value, str):
        return value.lower() in ("true", "1", "t", "on", "yes", "y")
    if isinstance(value, bool):
        return value
    return False


@implementer(IPublishTraverse)
class BannerGet(Service):
    """Banner GET"""

    def get_rancher_metadata(self, url):
        """Returns Rancher metadata API"""
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with closing(urllib.request.urlopen(req, timeout=TIMEOUT)) as conn:
                result = json.loads(conn.read())
        except Exception:
            result = []
        return result

    def get_stacks(self):
        """Returns all Rancher stacks from the current environment"""
        url = "%s/stacks" % RANCHER_METADATA
        return self.get_rancher_metadata(url)

    # @cache(lambda *args: "rancher-status", lifetime=MEMCACHE_AGE)
    def get_stacks_status(self, stacks):
        """Returns status of required stacks"""
        status = None
        rancher_stacks = self.get_stacks()
        for stack in rancher_stacks:
            if stack.get("system") or stack.get("name") not in stacks:
                continue
            services = stack.get("services", [])
            if not services:
                continue
            for service in services:
                if not status and service.get("state") != "active":
                    status = service.get("state")
                    break
        return status

    def reply(self):
        """Reply"""

        if not IEeaBannerLayer.providedBy(self.request):
            return {
                "static_banner": {"enabled": False},
                "dynamic_banner": {"enabled": False},
            }
        development = self.request.form.get("development")

        dynamic_banner_env = "DYNAMIC_BANNER_ENABLED_" + getSite().getId()
        dynamic_banner_enabled = isTrue(
            os.getenv(dynamic_banner_env, False)
        ) or api.portal.get_registry_record(
            "dynamic_banner_enabled",
            interface=IBannerSettings,
            default=False,
        )

        static_banner_env = "STATIC_BANNER_ENABLED_" + getSite().getId()
        static_banner_enabled = isTrue(
            os.getenv(static_banner_env, False)
        ) or api.portal.get_registry_record(
            "static_banner_enabled",
            interface=IBannerSettings,
            default=False,
        )

        return {
            "static_banner": {
                "enabled": static_banner_enabled,
                "visible_to_all": api.portal.get_registry_record(
                    "static_banner_visible_to_all",
                    interface=IBannerSettings,
                    default=False,
                ),
                "type": api.portal.get_registry_record(
                    "static_banner_type", interface=IBannerSettings, default=""
                ),
                "title": api.portal.get_registry_record(
                    "static_banner_title",
                    interface=IBannerSettings,
                    default="",
                ),
                "message": api.portal.get_registry_record(
                    "static_banner_message",
                    interface=IBannerSettings,
                    default="",
                ),
            },
            "dynamic_banner": {
                "enabled": dynamic_banner_enabled,
                "visible_to_all": api.portal.get_registry_record(
                    "dynamic_banner_visible_to_all",
                    interface=IBannerSettings,
                    default=False,
                ),
                "title": api.portal.get_registry_record(
                    "dynamic_banner_title",
                    interface=IBannerSettings,
                    default="",
                ),
                "message": api.portal.get_registry_record(
                    "dynamic_banner_message",
                    interface=IBannerSettings,
                    default="",
                ),
                "rancher_stacks_status": None
                if development or not dynamic_banner_enabled
                else self.get_stacks_status(
                    api.portal.get_registry_record(
                        "rancher_stacks", interface=IBannerSettings, default=[]
                    )
                    or []
                ),
            },
        }
