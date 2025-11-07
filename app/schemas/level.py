from apiflask import Schema
from apiflask.fields import Boolean, DateTime, Enum, Integer, List, Nested, String

from app.db.models.level import (
    Level,
    LevelDifficulty,
    LevelLength,
    LevelRating,
    LevelType,
)
from app.schemas.creator import CreatorOut
from app.schemas.credit import LevelCreditOut


class LevelIn(Schema):
    GD_id = Integer()
    name = String()
    GD_publisher = String()
    level_type = Enum(LevelType)
    length = Enum(LevelLength)
    rating = Enum(LevelRating)


class LevelPatch(Schema):
    GD_id = Integer()
    display_name = String()
    url_name = String()
    date_published = DateTime()
    GD_publisher = String()
    GD_difficulty = Enum(LevelDifficulty)
    level_type = Enum(LevelType)
    length = Enum(LevelLength)
    rating = Enum(LevelRating)
    is_megacollab = Boolean()
    is_upcoming = Boolean()


class LevelOutMin(Schema):
    class Meta:
        model = Level

    id = Integer()
    GD_id = Integer()
    display_name = String()
    url_name = String()
    GD_publisher = String()
    level_type = Enum(LevelType)
    length = Enum(LevelLength)
    rating = Enum(LevelRating)
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
