"""JsonSchema providers."""

from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from eea.schema.slate.field import ISlateJSONField
from plone.restapi.types.interfaces import IJsonSchemaProvider
from plone.restapi.types.adapters import DefaultJsonSchemaProvider


@adapter(ISlateJSONField, Interface, Interface)
@implementer(IJsonSchemaProvider)
class SlateJSONFieldSchemaProvider(DefaultJsonSchemaProvider):
    """Slate JSON Field Schema Provider"""

    def get_type(self):
        """Type"""
        return "array"

    def get_widget(self):
        """Widget"""
        return getattr(self.field, "widget", False) or "slate"

    def get_factory(self):
        """Factory"""
        return "SlateJSONField"
