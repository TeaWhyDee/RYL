from apiflask.fields import Date, Enum, Integer, Nested, String

from app.db.models.team_member import TeamRole
from app.db.models.user import UserRole
from app.schemas import RYLContentIn, RYLOut
from app.utility.validators import Authorized


# In
#
class TeamMemberIn(RYLContentIn):
    creator_id = Integer(required=True)
    team_id = Integer(required=True)
    role = Enum(TeamRole)
    date_joined = Date(required=False)
    date_left = Date(required=False)


# Patch
#
class TeamMemberPatch(RYLContentIn):
    role = Enum(TeamRole, validate=Authorized(UserRole.helper))
    date_joined = Date(required=False, validate=Authorized(UserRole.helper))
    date_left = Date(required=False, validate=Authorized(UserRole.helper))


# Out
#
class _TeamMemberOutMin(RYLOut):
    role = Enum(TeamRole)
    date_joined = Date()
    date_left = Date()


class TeamMemberOut(_TeamMemberOutMin):
    creator_id = Integer()
    team_id = Integer()


class TeamMemberOutExtra(_TeamMemberOutMin):
    team = Nested("TeamOut")
    creator = Nested("CreatorOut")
