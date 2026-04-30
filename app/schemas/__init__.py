"""
These schemas are used for CONTENT.
i.e. models derived from ContentBase.
Otherwise, use normal Schema.
"""

from apiflask import Schema
from apiflask.fields import DateTime, Integer, String, Enum
from apiflask.validators import Length

from app.db.database import CompletenessStatus


class RYLOutSchema(Schema):
    id = Integer()
    created_at = DateTime()
    updated_at = DateTime()
    completeness_status = Enum(enum=CompletenessStatus)


class RYLInSchema(Schema):
    note = String(required=False, validate=Length(1, 500))
