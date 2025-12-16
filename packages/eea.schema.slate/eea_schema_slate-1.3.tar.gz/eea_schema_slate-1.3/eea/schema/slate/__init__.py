"""Main product initializer"""

import logging
from zope.i18nmessageid.message import MessageFactory

_ = MessageFactory("eea")
logger = logging.getLogger("eea.schema.slate")

try:
    from plone.app.dexterity.browser.types import ALLOWED_FIELDS
    from plone.app.dexterity.browser.types import TypeSchemaContext
except ImportError:
    logger.info("Could not register SlateJSONField: plone.app.dexterity not installed")
else:
    slate = "eea.schema.slate.field.SlateJSONField"
    if slate not in TypeSchemaContext.allowedFields:
        TypeSchemaContext.allowedFields = ALLOWED_FIELDS + [slate]
