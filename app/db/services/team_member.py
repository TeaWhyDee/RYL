from datetime import date
from typing import Optional

from sqlalchemy import Date

from app import db
from app.db.database import CompletenessStatus
from app.db.models.team_member import TeamMember, TeamRole
from app.db.models.team import Team  # Import for validation
from app.utility.context import ContextValues
from app.utility.exceptions import RYLAlreadyExists

# Assuming these imports match your user structure or you have a separate Creator model
from app.db.models.creator import Creator


def get_team_member(id: int):
    team_member = TeamMember.query.filter_by(id=id).one_or_none()

    return team_member


def try_add_team_member(
    ctx: ContextValues,
    team_id: int,
    creator_id: int,
    role: TeamRole,
    date_joined: Optional[Date] = None,
    date_left: Optional[Date] = None,
):
    """
    Attempts to add a team member.
    Checks that the Team and Creator exist before creating the link.
    """
    # Validate Team exists
    team = Team.query.get(team_id)
    if not team:
        raise RYLAlreadyExists(f"Team with ID {team_id} not found")

    # Validate Creator exists
    creator = Creator.query.get(creator_id)
    if not creator:
        raise RYLAlreadyExists(f"Creator with ID {creator_id} not found")

    # Prevent adding if already a member of this specific team
    # Note: Strict equality check on FKs is efficient
    existing_member = TeamMember.query.filter_by(
        team_id=team_id, creator_id=creator_id
    ).one_or_none()

    if existing_member:
        raise RYLAlreadyExists(
            f"Creator {creator_id} already belongs to Team {team_id}"
        )

    new_member = TeamMember(
        team_id=team_id,
        creator_id=creator_id,
        role=role,
        date_joined=date_joined,
        date_left=date_left,
    )

    ctx.set()
    db.session.add(new_member)
    db.session.commit()

    return new_member


def find_by_ids(team_id: int, creator_id: int) -> Optional[TeamMember]:
    """
    Helper to fetch an existing member by both IDs.
    Used internally or if a GET endpoint is implemented later.
    """
    return TeamMember.query.filter_by(
        team_id=team_id, creator_id=creator_id
    ).one_or_none()
