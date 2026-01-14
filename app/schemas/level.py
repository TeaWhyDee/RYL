from apiflask import Schema
from apiflask.fields import (
    Boolean,
    DateTime,
    Enum,
    Integer,
    Nested,
    String,
)

from app.db.models.level import (
    GDDifficulty,
    GDLength,
    GDRating,
    GDVersion,
    Level,
    LevelType,
)
from app.schemas.author import AuthorCreatorOutExtra, AuthorTeamOutExtra
from app.schemas.creator import CreatorOut, TeamOut
from app.schemas.credit import CreditOut, CreditOutCreatorExtra

# from app.schemas.credit import LevelCreditOut


class LevelIn(Schema):
    GD_id = Integer()
    name = String()
    GD_publisher = String()
    level_type = Enum(LevelType)
    length = Enum(GDLength)
    rating = Enum(GDRating)


class LevelPatch(Schema):
    GD_id = Integer()
    display_name = String()
    url_name = String()
    date_published = DateTime()
    GD_publisher = String()
    GD_difficulty = Enum(GDDifficulty)
    level_type = Enum(LevelType)
    length = Enum(GDLength)
    rating = Enum(GDRating)
    is_megacollab = Boolean()
    is_upcoming = Boolean()


class LevelOutMin(Schema):
    class Meta:
        model = Level

    id = Integer()
    GD_id = Integer()
    url_name = String()
    display_name = String()

    date_published = DateTime()
    GD_publisher = String()
    GD_difficulty = Enum(GDDifficulty)
    GD_version = Enum(GDVersion)
    GD_length = Enum(GDLength)
    GD_rating = Enum(GDRating)

    level_type = Enum(LevelType)
    is_megacollab = Boolean()
    is_upcoming = Boolean()

    url = String()


class LevelOut(LevelOutMin):  # output only ids (of credits, creators, teams)
    author_creators = Nested(CreatorOut, many=True)
    author_teams = Nested(TeamOut, many=True)
    credits = Nested(CreditOut, many=True)


class LevelOutExtra(LevelOutMin):  # output full schemas (creator, team, credit)
    class Meta:
        include_relationships = True

    author_creators = Nested(AuthorCreatorOutExtra, many=True)
    author_teams = Nested(AuthorTeamOutExtra, many=True)
    credits = Nested(CreditOutCreatorExtra, many=True)
