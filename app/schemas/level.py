from apiflask import Schema
from apiflask.fields import (
    Boolean,
    Date,
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
from app.schemas import RYLContentIn, RYLContentOut
from app.schemas.credit import LevelCreditOut, LevelCreditOutExtra
from app.schemas.genre import GenreOut
from app.schemas.level_authorship import (
    LevelAuthorshipOut,
    LevelAuthorshipOutExtra,
)
from app.schemas.level_upload import LevelUploadOut


# in
class LevelInGD(Schema):
    GD_id = Integer(required=True, validate=Length(10, 20))
    level_type = Enum(LevelType)
    description = String(required=False, validate=Length(1, 5000))


class LevelIn(RYLContentIn):
    """
    Schema for creating or providing core info for a Level
    (used when GD_id might be handled by the API).
    """

    name = String(required=True, validate=Length(1, 50))
    description = String(required=False, validate=Length(1, 5000))
    level_type = Enum(LevelType, required=True)
    is_two_player = Boolean(required=False)

    date_showcased = Date(required=False)
    date_published = Date(required=False)

    length = Enum(LevelLength, required=False)
    length_seconds = Integer(required=False)

    GD_rating = Enum(LevelRating, required=False)
    GD_difficulty = Enum(LevelDifficulty, required=False)
    GD_version = Enum(GDVersion, required=False)

    is_megacollab = Boolean(required=False)
    is_upcoming = Boolean(required=False)


class LevelPatch(RYLContentIn):
    GD_id = Integer()
    display_name = String()
    url_name = String()
    description = String()
    level_type = Enum(LevelType)
    is_two_player = Boolean()

    date_showcased = Date()
    date_published = Date()

    length = Enum(LevelLength)
    length_seconds = Integer()

    GD_rating = Enum(LevelRating)
    GD_difficulty = Enum(LevelDifficulty)
    GD_version = Enum(GDVersion)

    video_url = String()
    thumbnail_url = String()
    is_upcoming = Boolean()
    is_megacollab = Boolean()


# out
class LevelOutMin(RYLContentOut):
    class Meta:
        model = Level

    id = Integer()
    GD_id = Integer()
    display_name = String()
    url_name = String()
    description = String()
    level_type = Enum(LevelType)
    is_two_player = Boolean()
    #
    date_showcased = Date()
    date_published = Date()
    #
    length = Enum(LevelLength)
    length_seconds = Integer()
    #
    GD_rating = Enum(LevelRating)
    GD_difficulty = Enum(LevelDifficulty)
    GD_version = Enum(GDVersion)
    #
    video_url = String()
    thumbnail_url = String()
    is_upcoming = Boolean()
    is_megacollab = Boolean()
    #


class LevelOut(LevelOutMin):
    url = String()
    # creator_id = Integer()


class LevelOutExtra(LevelOutMin):
    class Meta:
        model = Level
        include_relationships = True

    credits = Nested(LevelCreditOutExtra, many=True)
    authorships = Nested(LevelAuthorshipOutExtra, many=True)
    uploads = Nested(LevelUploadOut, many=True)
    genres = Nested(GenreOut, many=True)
    # song
