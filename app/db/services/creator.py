from typing import Optional

from app.db.database import CompletenessStatus, db
from app.db.models.creator import Creator
from app.utility.context import ContextValues
from app.utility.exceptions import RYLAlreadyExists
from app.utility.util import sanitize_for_url


def get_creator(id: int):
    creator = Creator.query.filter_by(id=id).one_or_none()

    return creator


def add_or_get_creator(
    ctx: ContextValues,
    creator_name: str,
    completeness_status: CompletenessStatus,
    description: Optional[str] = None,
):
    """
    Only use for one-off tasks.
    """
    creator = Creator.query.filter_by(display_name=creator_name).one_or_none()
    if creator:
        return creator

    new_creator = try_add_creator(
        ctx=ctx,
        name=creator_name,
        completeness_status=completeness_status,
        description=description,
    )

    return new_creator


def try_add_creator(
    ctx: ContextValues,
    name: str,
    completeness_status: CompletenessStatus,
    description: Optional[str] = None,
):
    creator = Creator.query.filter_by(display_name=name).one_or_none()
    if creator:
        raise RYLAlreadyExists(
            f"Creator with name {name} already exists: id {creator.id}"
        )

    url_name = sanitize_for_url(name)

    new_creator = Creator(
        display_name=name,
        url_name=url_name,
        completeness_status=completeness_status,
        description=description,
    )

    ctx.set()
    db.session.add(new_creator)
    db.session.commit()

    return new_creator
