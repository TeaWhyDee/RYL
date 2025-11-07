from typing import Optional

from app.db.database import db
from app.db.models.creator import Creator
from app.utility.context import ContextValues


def add_or_get_creator(
    context_values: ContextValues,
    creator_name: str,
):
    creator = Creator.query.filter_by(display_name=creator_name).one_or_none()
    if creator:
        return creator

    new_creator = Creator(name=creator_name)
    db.session.add(new_creator)

    context_values.set()
    db.session.add(new_creator)
    db.session.commit()

    return new_creator
