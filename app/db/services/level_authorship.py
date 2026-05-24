from typing import Optional

from app import db
from app.db.models.creator import Creator
from app.db.models.level import Level
from app.db.models.level_authorship import LevelAuthorship
from app.db.models.team import Team
from app.utility.context import ContextValues
from app.utility.exceptions import (
    RYLAlreadyExists,
    RYLInternalError,
    RYLNotFound,
)


def get_level_authorship(
    level_id: int,
    creator_id: Optional[int] = None,
    team_id: Optional[int] = None,
):
    query = LevelAuthorship.query.filter_by(level_id=level_id)

    if creator_id is not None:
        query = query.filter(LevelAuthorship.creator_id == creator_id)
    elif team_id is not None:
        query = query.filter(LevelAuthorship.team_id == team_id)

    return query.one_or_none()


def add_or_get_level_authorship(
    ctx: ContextValues,
    level_id: int,
    creator_id: Optional[int] = None,
    team_id: Optional[int] = None,
):
    level_authorship = get_level_authorship(level_id, creator_id)

    if not level_authorship:
        if creator_id:
            try_add_level_authorship(ctx, level_id, creator_id=creator_id)
        elif team_id:
            try_add_level_authorship(ctx, level_id, team_id=team_id)


def try_add_level_authorship(
    ctx: ContextValues,
    level_id: int,
    creator_id: Optional[int] = None,
    team_id: Optional[int] = None,
):
    if creator_id and team_id:
        raise RYLInternalError(
            "Cannot create level author with both team and creator."
        )

    # Verify level exists
    level = Level.query.filter_by(id=level_id).one_or_none()
    if not level:
        raise RYLNotFound(f"Level with id {level_id} not found")

    # Check creator or team exists
    if creator_id:
        creator = Creator.query.filter_by(id=creator_id).one_or_none()
        if not creator:
            raise RYLNotFound(f"Creator with id {creator_id} not found")

        existing_author = LevelAuthorship.query.filter_by(
            level_id=level_id, creator_id=creator_id
        ).one_or_none()

        if existing_author:
            raise RYLAlreadyExists(
                f"Level Authorship already exists. (creator_id: {creator_id}, level_id: {level_id}, id: {existing_author.id})"
            )

    if team_id:
        team = Team.query.filter_by(id=team_id).one_or_none()
        if not team:
            raise RYLNotFound(f"Team with id {team_id} not found")

        existing_author = LevelAuthorship.query.filter_by(
            level_id=level_id, team_id=team_id
        ).one_or_none()

        if existing_author:
            raise RYLAlreadyExists(
                f"Level Author credit with team {team_id} and level {level_id} already exists: id {existing_author.id}"
            )

    # All good, create new author

    new_author = LevelAuthorship(
        level_id=level_id,
        creator_id=creator_id,
        team_id=team_id,
    )

    ctx.set()
    db.session.add(new_author)
    db.session.commit()

    return new_author
