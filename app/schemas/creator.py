from apiflask.fields import Integer, Nested, String
from apiflask.validators import Length
from marshmallow.validate import And

from app.db.models.user import UserRole
from app.schemas import RYLContentIn, RYLContentOut
from app.utility.validators import Authorized


#
# In
#
class CreatorIn(RYLContentIn):
    display_name = String(required=True, validate=Length(1, 50))
    description = String(required=False, validate=Length(1, 5000))


#
# Patch
#
class CreatorPatch(RYLContentIn):
    display_name = String(
        validate=And(Length(1, 50), Authorized(UserRole.moderator))
    )
    url_name = String(
        validate=And(Length(1, 60), Authorized(UserRole.moderator))
    )
    description = String(
        validate=And(Length(1, 5000), Authorized(auth_level=UserRole.helper))
    )


#
# Out
#
class _CreatorOutMin(RYLContentOut):
    display_name = String()
    url_name = String()
    description = String()


class CreatorOut(_CreatorOutMin):
    pass


class CreatorOutExtra(_CreatorOutMin):
    team_memberships = Nested("TeamMemberOut", many=True)
    credits = Nested("LevelCreditOut", many=True)
    # TODO
