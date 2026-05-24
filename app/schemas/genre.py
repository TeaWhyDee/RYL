from apiflask.fields import Integer, List, String
from apiflask.validators import Length
from marshmallow.validate import And

from app.db.models.genre import Genre
from app.db.models.user import UserRole
from app.schemas import RYLContentIn, RYLOut
from app.utility.validators import Authorized


class GenreIn(RYLContentIn):
    name = String(
        required=True,
        validate=And(Length(1, 50), Authorized(UserRole.moderator)),
    )
    description = String(required=False, validate=Length(0, 500))


class GenrePatch(RYLContentIn):
    display_name = String(
        validate=And(Length(1, 50), Authorized(UserRole.moderator))
    )
    url_name = String(validate=And(Length(1, 60), Authorized(UserRole.admin)))
    description = String(validate=Length(0, 500))


class GenreOut(RYLOut):
    display_name = String()
    url_name = String()
    description = String()
