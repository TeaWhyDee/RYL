from apiflask.fields import Enum, Integer, String
from apiflask.validators import Length
from marshmallow.validate import And

from app.db.models.level import GDVersion
from app.db.models.user import UserRole
from app.schemas import RYLContentIn, RYLOut
from app.utility.validators import Authorized


class GDServerIn(RYLContentIn):
    name = String(
        required=True,
        validate=And(Length(1, 60), Authorized(UserRole.moderator)),
    )  # converted to url_name
    description = String(
        required=False,
        validate=And(Length(0, 5000), Authorized(UserRole.moderator)),
    )
    IP = String(
        required=True,
        validate=And(Length(1, 45), Authorized(UserRole.moderator)),
    )
    GD_version = Enum(GDVersion)


class GDServerPatch(RYLContentIn):
    display_name = String(
        validate=And(Length(1, 50), Authorized(UserRole.moderator))
    )
    url_name = String(validate=And(Length(1, 60), Authorized(UserRole.admin)))
    description = String(
        validate=And(Length(0, 5000), Authorized(UserRole.moderator))
    )


# class GDServerOutMin(RYLOutSchema):
#     display_name = String()
#     url_name = String()
#     GD_version = Enum(enum=GDVersion)


class GDServerOut(RYLOut):
    display_name = String()
    description = String()
    url_name = String()
    GD_version = Enum(enum=GDVersion)
    IP = String()
