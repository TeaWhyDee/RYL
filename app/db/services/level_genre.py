from typing import List, Optional, Tuple

from app import db
from app.db.models.genre import Genre
from app.db.models.level_genre import LevelGenre
from app.utility.context import ContextValues
from app.utility.exceptions import RYLNotFound


def get_level_genre(id: int):
    level_genre = LevelGenre.query.filter_by(id=id).one_or_none()
    return level_genre


def get_level_genres(
    level_id: int,
    genre_id: Optional[int] = None,
) -> Optional[List[LevelGenre]]:
    """Get associations. If genre_id provided, narrow scope."""

    query = LevelGenre.query.filter_by(level_id=level_id)
    if genre_id is not None:
        query = query.filter_by(genre_id=genre_id)

    return query.all()


def try_add_level_genre(
    ctx: ContextValues,
    level_id: int,
    genre_id: int,
):
    new_association = LevelGenre(level_id=level_id, genre_id=genre_id)

    ctx.set()
    db.session.add(new_association)
    db.session.commit()

    return new_association


def delete_level_genre(ctx: ContextValues, level_id: int, genre_id: int):
    """Remove specific association."""
    existing = LevelGenre.query.filter_by(
        level_id=level_id, genre_id=genre_id
    ).one_or_none()

    if not existing:
        return RYLNotFound(
            f"Genre with level_id:{level_id} and genre_id:{genre_id} not found"
        )

    ctx.set()
    db.session.delete(existing)
    db.session.commit()
