from apiflask.fields import String
from apiflask.validators import Length
from marshmallow.validate import And

from app.db.models.user import UserRole
from app.schemas import RYLContentIn, RYLContentOut
from app.utility.validators import Authorized


# In
#
class TeamIn(RYLContentIn):
    name = String(
        required=True, validate=And(Length(1, 50), Authorized(UserRole.helper))
    )
    description = String(
        required=False,
        validate=And(Length(1, 5000), Authorized(UserRole.helper)),
    )


class TeamPatch(RYLContentIn):
    display_name = String(
        validate=And(Length(1, 50), Authorized(UserRole.helper))
    )
    url_name = String(
        validate=And(Length(1, 60), Authorized(UserRole.moderator))
    )
    description = String(
        validate=And(Length(1, 5000), Authorized(auth_level=UserRole.helper))
    )


# Out
#
class TeamOutMin(RYLContentOut):
    display_name = String()
    url_name = String()
    description = String()


class TeamOut(RYLContentOut):
    display_name = String()
    url_name = String()
    description = String()
