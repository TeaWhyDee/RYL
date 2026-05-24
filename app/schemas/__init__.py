"""
These schemas are used for CONTENT.
i.e. models derived from ContentBase.
Otherwise, use normal Schema.
"""

from apiflask import Schema
from apiflask.fields import DateTime, Enum, Integer, String
from apiflask.validators import Length

from app.db.database import CompletenessStatus


class RYLOut(Schema):
    id = Integer()
    created_at = DateTime()
    updated_at = DateTime()


class RYLContentOut(Schema):
    id = Integer()
    created_at = DateTime()
    updated_at = DateTime()
    completeness_status = Enum(enum=CompletenessStatus)
    note = String()


class RYLContentIn(Schema):
    note = String(required=False, validate=Length(0, 500))
