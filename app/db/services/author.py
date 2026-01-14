from app.db.database import db
from app.db.models.author import LevelAuthorCreator
from app.utility.context import ContextValues


def add_or_get_author_creator(
    context_values: ContextValues,
    level_id: int,
    creator_id: int,
):
    author = LevelAuthorCreator.query.filter_by(
        creator_id=creator_id, level_id=level_id
    ).one_or_none()
    if author:
        return author

    new_author = LevelAuthorCreator(
        level_id,
        creator_id,
    )

    context_values.set()
    db.session.add(new_author)
    db.session.commit()

    return new_author
