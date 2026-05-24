from apiflask.fields import Enum, Integer, Nested
from marshmallow.validate import And

from app.db.models.credit import LevelCreatorRole, LevelCredit
from app.db.models.user import UserRole
from app.schemas import RYLContentIn, RYLOut
from app.schemas.creator import CreatorOut
from app.utility.validators import Authorized


class LevelCreditIn(RYLContentIn):
    class Meta:
        model = LevelCredit

    level_id = Integer(required=True)
    creator_id = Integer(required=True)
    creator_role = Enum(LevelCreatorRole, required=True)


class LevelCreditPatch(RYLContentIn):
    creator_role = Enum(
        LevelCreatorRole,
        required=False,
        validate=Authorized(UserRole.helper),
    )


class LevelCreditOut(RYLOut):
    class Meta:
        model = LevelCredit

    level_id = Integer()
    creator_id = Integer()
    creator_role = Enum(LevelCreatorRole)


class LevelCreditOutExtra(RYLOut):
    class Meta:
        model = LevelCredit

    level_id = Integer()
    creator_id = Integer()
    creator_role = Enum(LevelCreatorRole)
    creator = Nested(CreatorOut)
