from typing import Optional

from app.db.database import db
from app.db.models.level import GDLength, GDRating, Level, LevelType
from app.utility.context import ContextValues


def add_or_get_level(
    context_values: ContextValues,
    level_GD_id: int,
    level_name: str,
    level_publisher: str,
    level_type: LevelType,
    level_length: Optional[GDLength] = None,
    level_rating: Optional[GDRating] = None,
):
    lvl = Level.query.filter_by(GD_id=level_GD_id).one_or_none()
    if lvl:
        return lvl

    new_level = Level(
        GD_id=level_GD_id,
        name=level_name,
        GD_publisher=level_publisher,
        level_type=level_type,
        level_length=level_length,
        level_rating=level_rating,
    )

    context_values.set()
    db.session.add(new_level)
    db.session.commit()

    return new_level
