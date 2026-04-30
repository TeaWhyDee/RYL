from typing import Optional

from app.db.database import CompletenessStatus, db
from app.db.models.level import Level, LevelLength, LevelRating, LevelType
from app.utility.context import ContextValues


def add_or_get_level(
    context_values: ContextValues,
    level_GD_id: int,
    level_name: str,
    # level_publisher_id: int,
    level_type: LevelType,
    completeness_status: CompletenessStatus,
    level_length: Optional[LevelLength] = None,
    level_rating: Optional[LevelRating] = None,
):
    lvl = Level.query.filter_by(GD_id=level_GD_id).one_or_none()
    if lvl:
        return lvl

    level_length_seconds = 60

    new_level = Level(
        GD_id=level_GD_id,
        name=level_name,
        level_type=level_type,
        level_length=level_length,
        level_length_seconds=level_length_seconds,
        level_rating=level_rating,
        completeness_status=completeness_status,
        # date_showcased=
        # date_published=
    )

    context_values.set()
    db.session.add(new_level)
    db.session.commit()

    return new_level
