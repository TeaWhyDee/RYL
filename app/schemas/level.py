from apiflask import Schema
from apiflask.fields import (
    Boolean,
    DateTime,
    Enum,
    Integer,
    Nested,
    String,
)
from apiflask.validators import Length

from app.db.models.level import (
    GDVersion,
    Level,
    LevelDifficulty,
    LevelLength,
    LevelRating,
    LevelType,
)
from app.schemas import RYLOutSchema
from app.schemas.credit import LevelCreditOut


# in
class LevelInGD(Schema):
    GD_id = Integer(required=True, validate=Length(10, 20))
    level_type = Enum(LevelType)


class LevelIn(Schema):
    """
    Schema for creating or providing core info for a Level
    (used when GD_id might be handled by the API).
    """

    name = String(required=True, validate=Length(1, 50))
    level_type = Enum(LevelType, required=True)

    date_published = DateTime(required=False)
    length = Enum(LevelLength, required=False)
    GD_rating = Enum(LevelRating, required=False)
    GD_difficulty = Enum(LevelDifficulty, required=False)
    GD_version = Enum(GDVersion, required=False)
    is_megacollab = Boolean(required=False)
    is_upcoming = Boolean(required=False)


class LevelPatch(Schema):
    GD_id = Integer()
    display_name = String()
    url_name = String()
    date_published = DateTime()
    GD_publisher_id = Integer()
    GD_difficulty = Enum(LevelDifficulty)
    level_type = Enum(LevelType)
    length = Enum(LevelLength)
    length_seconds = Integer()
    GD_rating = Enum(LevelRating)
    is_megacollab = Boolean()
    is_upcoming = Boolean()


class LevelDelete(Schema):
    id = Integer()


# out
class LevelOutMin(RYLOutSchema):
    class Meta:
        model = Level

    id = Integer()
    GD_id = Integer()
    display_name = String()
    url_name = String()
    GD_publisher_id = Integer()
    level_type = Enum(LevelType)
    length = Enum(LevelLength)
    GD_rating = Enum(LevelRating)
    is_upcoming = Boolean()
    is_megacollab = Boolean()


class LevelOut(LevelOutMin):
    url = String()
    # creator_id = Integer()


class LevelOutExtra(LevelOutMin):
    class Meta:
        model = Level
        include_relationships = True

    # creator = Nested(CreatorOut)
    credits = Nested(LevelCreditOut, many=True)
