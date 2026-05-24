from apiflask.fields import Enum, Integer, Nested, String
from apiflask.validators import Length
from marshmallow.validate import And

from app.db.models.level import GDVersion, LevelDifficulty, LevelRating
from app.db.models.user import UserRole
from app.schemas import RYLContentIn, RYLOut
from app.schemas.gd_account import GDAccountOut
from app.schemas.gd_server import GDServerOut
from app.utility.validators import Authorized


# Base schemas for input/output
class LevelUploadIn(RYLContentIn):
    gd_ID = Integer(
        required=True,
        validate=And(Length(1, 60), Authorized(UserRole.moderator)),
    )
    gd_title = String(
        required=True,
        validate=And(Length(1, 500), Authorized(UserRole.moderator)),
    )
    gd_rating = Enum(
        enum=LevelRating,
        validate=And(Length(1, 20), Authorized(UserRole.moderator)),
    )
    gd_difficulty = Enum(
        enum=LevelDifficulty,
        validate=And(Length(1, 20), Authorized(UserRole.moderator)),
    )
    gd_version_original = Enum(
        GDVersion,
        required=False,
        validate=And(Length(1, 20), Authorized(UserRole.moderator)),
    )
    gd_version_last = Enum(
        GDVersion,
        required=False,
        validate=And(Length(1, 20), Authorized(UserRole.moderator)),
    )
    song_NG_ID = Integer(
        required=True,
        validate=And(Length(1, 60), Authorized(UserRole.moderator)),
    )
    gd_Account_id = Integer(
        required=True,
        validate=And(Length(1, 60), Authorized(UserRole.moderator)),
    )
    level_id = Integer(
        required=False,
        validate=And(Length(1, 60), Authorized(UserRole.moderator)),
    )
    gd_server_id = Integer(
        required=True,
        validate=And(Length(1, 60), Authorized(UserRole.moderator)),
    )


class LevelUploadPatch(RYLContentIn):
    gd_title = String(
        validate=And(Length(1, 500), Authorized(UserRole.moderator))
    )
    gd_rating = String(
        validate=And(Length(1, 20), Authorized(UserRole.moderator))
    )
    gd_difficulty = String(
        validate=And(Length(1, 20), Authorized(UserRole.moderator))
    )
    gd_version_original = Enum(
        GDVersion,
        validate=And(Length(1, 20), Authorized(UserRole.moderator)),
    )
    gd_version_last = Enum(
        GDVersion,
        validate=And(Length(1, 20), Authorized(UserRole.moderator)),
    )


# Output schemas
class LevelUploadOutMin(RYLOut):
    gd_ID = Integer()
    gd_title = String()
    song_NG_ID = Integer()


class LevelUploadOut(RYLOut):
    gdID = Integer()
    gd_title = String()
    gd_rating = String()
    gd_difficulty = String()
    gd_version_original = Enum(GDVersion)
    gd_version_last = Enum(GDVersion)

    song_NG_ID = Integer()

    gd_cache_likes = Integer()
    note = String()

    gd_account_id = Integer()
    gd_server_id = Integer()
    level_id = Integer()


class LevelUploadOutExtra(LevelUploadOut):
    # assumes called from level
    gd_server = Nested(GDServerOut)
    gd_account = Nested(GDAccountOut)
