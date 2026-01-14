from app.db.database import db
from app.db.models.credit import LevelCredit, LevelCreditRole
from app.utility.context import ContextValues


def add_or_get_credit(
    context_values: ContextValues,
    level_id: int,
    creator_id: int,
    creator_role: LevelCreditRole,
):
    credit = LevelCredit.query.filter_by(
        creator_id=creator_id, level_id=level_id, creator_role=creator_role
    ).one_or_none()
    if credit:
        return credit

    new_credit = LevelCredit(
        level_id,
        creator_id,
        creator_role,
    )

    context_values.set()
    db.session.add(new_credit)
    db.session.commit()

    return new_credit
