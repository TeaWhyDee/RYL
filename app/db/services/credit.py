from typing import Optional

from app.db.database import db
from app.db.models.credit import LevelCreatorRole, LevelCredit
from app.utility.context import ContextValues
from app.utility.exceptions import RYLAlreadyExists


def get_credit(id: int):
    credit = LevelCredit.query.filter_by(id=id).one_or_none()

    return credit


def find_credit(level_id: int, creator_id: int, role: LevelCreatorRole):
    query = (
        LevelCredit.query.filter_by(level_id=level_id)
        .filter_by(creator_id=creator_id)
        .filter_by(creator_role=role)
    )

    return query.all()


def try_add_credit(
    ctx: ContextValues,
    level_id: int,
    creator_id: int,
    creator_role: LevelCreatorRole,
):
    existing_credit = LevelCredit.query.filter_by(
        level_id=level_id,
        creator_id=creator_id,
        creator_role=creator_role,
    ).one_or_none()

    if existing_credit:
        raise RYLAlreadyExists(
            f"This credit already exists: id {existing_credit.id}"
        )

    new_credit = LevelCredit(
        level_id=level_id,
        creator_id=creator_id,
        creator_role=creator_role,
    )

    ctx.set()
    db.session.add(new_credit)
    db.session.commit()

    return new_credit
