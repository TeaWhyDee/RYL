from apiflask.fields import String
from apiflask.validators import Length
from marshmallow.validate import And
from app.db.models.user import UserType
from app.schemas import RYLInSchema, RYLOutSchema
from app.utility.validators import Authorized


class TeamIn(RYLInSchema):
    name = String(
        required=True, validate=And(Length(1, 50), Authorized(UserType.helper))
    )
    description = String(
        required=False,
        validate=And(Length(1, 5000), Authorized(UserType.helper)),
    )


class TeamPatch(RYLInSchema):
    display_name = String(
        validate=And(Length(1, 50), Authorized(UserType.helper))
    )
    url_name = String(
        validate=And(Length(1, 60), Authorized(UserType.moderator))
    )
    description = String(
        validate=And(Length(1, 5000), Authorized(auth_level=UserType.helper))
    )


# out
class TeamOutMin(RYLOutSchema):
    display_name = String()
    url_name = String()
    description = String()


class TeamOut(RYLOutSchema):
    display_name = String()
    url_name = String()
    description = String()
