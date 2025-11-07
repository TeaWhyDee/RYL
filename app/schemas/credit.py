from apiflask import APIFlask, Schema
from apiflask.fields import Boolean, Enum, Integer, List, Nested, String

from app.db.models.credit import LevelCreatorRole, LevelCredit
from app.schemas.creator import CreatorOut


class LevelCreditIn(Schema):
    class Meta:
        model = LevelCredit

    level_id = Integer()
    creator_id = Integer()
    creator_role = Enum(LevelCreatorRole)


class LevelCreditOut(Schema):
    class Meta:
        model = LevelCredit

    id = Integer()
    creator = Nested(CreatorOut)
    creator_role = Enum(LevelCreatorRole)


class LevelCreditOutFull(Schema):
    class Meta:
        model = LevelCredit

    id = Integer()
    level_id = Integer()
    creator_id = Integer()
    creator_role = Enum(LevelCreatorRole)
