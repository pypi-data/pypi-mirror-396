"""Module where all interfaces, events and exceptions live."""

from zope import schema
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from eea.banner import EEAMessageFactory as _


class IEeaBannerLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IBannerSettings(Interface):
    """Client settings for EEA Banner."""

    static_banner_enabled = schema.Bool(
        title=_("Enable / disable static banner"),
        description=_(
            "If STATIC_BANNER_ENABLED environment variable is 'on' "
            "this flag has no effect"
        ),
        default=True,
        required=False,
    )

    static_banner_visible_to_all = schema.Bool(
        title=_("Show static banner to anonymous users?"),
        default=True,
        required=False,
    )

    static_banner_type = schema.Choice(
        title=_("Static banner type"),
        default="warning",
        vocabulary=SimpleVocabulary.fromValues(["success", "warning", "error"]),
    )

    static_banner_title = schema.TextLine(
        title=_("Static banner title"),
        default="This is a demo/test instance",
        required=False,
    )

    static_banner_message = schema.Text(
        title=_("Static banner message"),
        required=False,
        default=(
            "Do not use it for operational purposes. "
            "All changes will be regularly overwritten"
        ),
    )

    dynamic_banner_enabled = schema.Bool(
        title=_("Enable / disable dynamic banner"),
        default=True,
        required=False,
        description=_(
            "It will appear only if status of at least one stack "
            "is not 'active'. "
            "If STATIC_BANNER_ENABLED environment variable is 'on' "
            "this flag has no effect"
        ),
    )

    dynamic_banner_visible_to_all = schema.Bool(
        title=_("Show dynamic banner to anonymous users?"),
        default=True,
        required=False,
    )

    rancher_stacks = schema.List(
        title=_("Rancher stacks to monitor"),
        default=[],
        required=False,
        value_type=schema.TextLine(),
    )

    dynamic_banner_title = schema.TextLine(
        title=_("Dynamic banner title"),
        default="Web admins says:",
        required=False,
    )

    dynamic_banner_message = schema.Text(
        title=_("Dynamic banner message"),
        required=False,
        default="The system is {}",
        description=(
            "Add suffix/prefix to rancher stacks status message. "
            "Use {} for rancher stacks status placeholder"
        ),
    )
