from apiflask import Schema
from apiflask.fields import Integer, String
from apiflask.validators import Length
from marshmallow.validate import And

from app.db.models.user import UserRole
from app.schemas import RYLContentIn, RYLOut
from app.utility.validators import Authorized


class GDAccountIn(RYLContentIn):
    username = String(required=True, validate=Length(1, 50))
    gd_account_gdid = Integer(required=True)
    gd_server_id = Integer(required=True)


class GDAccountPatch(RYLContentIn):
    username = String(
        required=False,
        validate=And(Length(1, 50), Authorized(UserRole.moderator)),
    )
    gd_account_gdid = Integer(
        required=False, validate=Authorized(UserRole.moderator)
    )
    gd_server_id = Integer(
        required=False, validate=Authorized(UserRole.moderator)
    )


class GDAccountOut(RYLOut):
    username = String()
    gd_account_gdid = Integer()
    gd_server_id = Integer()
