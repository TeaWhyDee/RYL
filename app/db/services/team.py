from typing import Optional

from app import db
from app.db.database import CompletenessStatus
from app.db.models.team import Team
from app.utility.context import ContextValues
from app.utility.exceptions import RYLAlreadyExists
from app.utility.util import sanitize_for_url


def get_team(id: int):
    team = Team.query.filter_by(id=id).one_or_none()

    return team


def try_add_team(
    ctx: ContextValues,
    name: str,
    completeness_status: CompletenessStatus,
    description: Optional[str] = None,
):
    team = Team.query.filter_by(display_name=name).one_or_none()
    if team:
        raise RYLAlreadyExists(
            f"Team with name {name} already exists: id {team.id}"
        )

    url_name = sanitize_for_url(name)

    new_team = Team(
        url_name=url_name,
        display_name=name,
        completeness_status=completeness_status,
        description=description if description else "...",
    )

    ctx.set()
    db.session.add(new_team)
    db.session.commit()

    return new_team
