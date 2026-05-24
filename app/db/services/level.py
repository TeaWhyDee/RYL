from datetime import date
from typing import Optional

from sqlalchemy import Date

from app.db.database import CompletenessStatus, db
from app.db.models.level import (
    GDVersion,
    Level,
    LevelDifficulty,
    LevelLength,
    LevelRating,
    LevelType,
)
from app.utility.context import ContextValues
from app.utility.exceptions import RYLAlreadyExists
from app.utility.util import get_url_name, sanitize_for_url


def get_level(id: int):
    level = Level.query.filter_by(id=id).one_or_none()

    return level


def get_level_by_url_name(url_name: str):
    level = Level.query.filter_by(url_name=url_name).one_or_none()

    return level


def try_add_level(
    ctx: ContextValues,
    level_GD_id: int,
    level_name: str,
    # level_publisher_id: int,
    level_type: LevelType,
    completeness_status: CompletenessStatus,
    level_length: Optional[LevelLength] = None,
    level_length_seconds: Optional[int] = None,
    level_rating: Optional[LevelRating] = None,
    description: Optional[str] = None,
    is_two_player: bool = False,
    #
    gd_version: Optional[GDVersion] = None,
    gd_difficulty: Optional[LevelDifficulty] = None,
    #
    date_published: Optional[date] = None,
    video_url: Optional[str] = None,
    thumbnail_url: Optional[str] = None,
):
    level = Level.query.filter_by(GD_id=level_GD_id).one_or_none()

    if level:
        raise RYLAlreadyExists(
            f"Level with ID {level_GD_id} already exists: id {level.id}"
        )

    url_name = get_url_name(level_name, Level.query)

    new_level = Level(
        GD_id=level_GD_id,
        url_name=url_name,
        display_name=level_name,
        level_type=level_type,
        level_length=level_length,
        level_length_seconds=level_length_seconds,
        level_rating=level_rating,
        completeness_status=completeness_status,
        description=description,
        gd_version=gd_version,
        gd_difficulty=gd_difficulty,
        is_two_player=is_two_player,
        date_published=date_published,
        #
        video_url=video_url,
        thumbnail_url=thumbnail_url,
    )

    ctx.set()
    db.session.add(new_level)
    db.session.commit()

    return new_level
