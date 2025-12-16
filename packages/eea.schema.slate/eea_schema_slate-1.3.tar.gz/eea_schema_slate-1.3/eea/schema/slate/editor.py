"""z3c.form editor"""

from plone.schemaeditor.fields import FieldFactory
from zope.interface import Attribute
from eea.schema.slate.field import ISlateJSONField
from eea.schema.slate.field import SlateJSONField
from eea.schema.slate import _


class ISlateJSON(ISlateJSONField):
    """Slate JSON"""

    # prevent some settings from being included in the field edit form
    default = Attribute("")


SlateJSONFactory = FieldFactory(SlateJSONField, _("SlateJSONField"))
