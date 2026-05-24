from typing import List, Optional

from app import db
from app.db.models.genre import Genre
from app.utility.context import ContextValues
from app.utility.exceptions import RYLNotFound
from app.utility.util import sanitize_for_url


def get_genre(id: int):
    genre = Genre.query.filter_by(id=id).one_or_none()
    return genre


def get_genres_by_url_name(url_name: str):
    """Get single genre by unique url_name."""
    return Genre.query.filter_by(url_name=url_name).first()


def try_add_genre(
    ctx: ContextValues,
    name: str,
    description: Optional[str] = None,
):
    url_name = sanitize_for_url(name)

    new_genre = Genre(
        name=name,
        display_name=name,
        url_name=url_name,
        description=description,
    )

    ctx.set()
    db.session.add(new_genre)
    db.session.commit()

    return new_genre


def delete_genre(ctx: ContextValues, id: int):
    genre = get_genre(id)

    if not genre:
        raise RYLNotFound(f"Genre {genre} not found")

    ctx.set()
    db.session.delete(genre)
    db.session.commit()
