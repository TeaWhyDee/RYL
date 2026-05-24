from apiflask import Schema
from apiflask.fields import Integer, Nested, String
from apiflask.validators import Length
from marshmallow.validate import And

from app.db.models.user import UserRole
from app.schemas import RYLContentIn, RYLOut
from app.schemas.creator import CreatorOut
from app.schemas.team import TeamOut
from app.utility.validators import Authorized


class LevelAuthorshipIn(RYLContentIn):
    level_id = Integer(required=True)
    creator_id = Integer(required=False)
    team_id = Integer(required=False)


class LevelAuthorshipPatch(RYLContentIn):
    author_alias_id = Integer(
        required=True, validate=Authorized(UserRole.helper)
    )


class LevelAuthorshipOut(RYLOut):
    id = Integer()
    level_id = Integer()
    creator_id = Integer()
    team_id = Integer()


class LevelAuthorshipOutExtra(LevelAuthorshipOut):
    creator = Nested(CreatorOut)
    team = Nested(TeamOut)
