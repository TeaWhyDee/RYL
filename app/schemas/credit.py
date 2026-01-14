from apiflask import Schema
from apiflask.fields import Enum, Integer, Nested

from app.db.models.credit import LevelCredit, LevelCreditRole


class CreditIn(Schema):
    class Meta:
        model = LevelCredit

    level_id = Integer()
    creator_id = Integer()
    creator_role = Enum(LevelCreditRole)


class CreditOut(Schema):
    class Meta:
        model = LevelCredit

    id = Integer()
    level_id = Integer()
    creator_id = Integer()
    creator_role = Enum(LevelCreditRole)


class CreditOutLevelExtra(Schema):
    class Meta:
        model = LevelCredit

    id = Integer()
    level = Nested("LevelOut")
    creator_role = Enum(LevelCreditRole)


class CreditOutCreatorExtra(Schema):
    class Meta:
        model = LevelCredit

    id = Integer()
    creator = Nested("CreatorOut")
    creator_role = Enum(LevelCreditRole)
