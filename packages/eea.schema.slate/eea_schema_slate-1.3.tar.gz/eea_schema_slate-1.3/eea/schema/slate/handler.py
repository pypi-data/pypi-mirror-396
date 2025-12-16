"""Slate JSON Field"""

from plone.supermodel.exportimport import BaseHandler
from eea.schema.slate.field import SlateJSONField


SlateJSONHandler = BaseHandler(SlateJSONField)
