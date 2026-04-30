from apiflask.fields import Enum, Integer, Nested

from app.db.models.credit import LevelCreatorRole, LevelCredit
from app.schemas import RYLInSchema, RYLOutSchema
from app.schemas.creator import CreatorOut


class LevelCreditIn(RYLInSchema):
    class Meta:
        model = LevelCredit

    level_id = Integer()
    creator_id = Integer()
    creator_role = Enum(LevelCreatorRole)


class LevelCreditOut(RYLOutSchema):
    class Meta:
        model = LevelCredit

    id = Integer()
    creator = Nested(CreatorOut)
    creator_role = Enum(LevelCreatorRole)


class LevelCreditOutFull(RYLOutSchema):
    class Meta:
        model = LevelCredit

    id = Integer()
    level_id = Integer()
    creator_id = Integer()
    creator_role = Enum(LevelCreatorRole)
