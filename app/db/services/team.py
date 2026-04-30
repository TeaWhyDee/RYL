from typing import Optional
from app import db
from app.db.database import CompletenessStatus
from app.db.models.team import Team
from app.utility.context import ContextValues
from app.utility.exceptions import RYLAlreadyExists


# def add_or_get_team(
#     context_values: ContextValues, name: str, description: Optional[str] = None
# ):
#     team = Team.query.filter_by(display_name=name).one_or_none()
#     if team:
#         return team
#
#     new_team = Team(name=name, description=description)
#
#     context_values.set()
#     db.session.add(new_team)
#     db.session.commit()
#
#     return new_team


def try_add_team(
    ctx: ContextValues,
    name: str,
    completeness_status: CompletenessStatus,
    description: Optional[str] = None,
):
    team = Team.query.filter_by(display_name=name).one_or_none()
    if team:
        raise RYLAlreadyExists("Team already exists")

    new_team = Team(
        name=name,
        completeness_status=completeness_status,
        description=description,
    )

    ctx.set()
    db.session.add(new_team)
    db.session.commit()

    return new_team
