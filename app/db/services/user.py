from typing import Optional

from app.db.database import db
from app.db.models.user import User, UserRole
from app.utility.context import ContextValues
from app.utility.exceptions import RYLBadPassword, RYLBadUsername
from app.utility.util import (
    password_sanity_check,
    sanitize_for_url,
    string_sanity_check,
)


def get_user(id: int):
    user = User.query.filter_by(id=id).one_or_none()

    return user


def add_or_get_user(
    ctx: ContextValues,
    id: int,
    username: Optional[str],
    password: Optional[str],
    email: Optional[str],
):
    user = User.query.filter_by(id=id).one_or_none()
    if user:
        return user

    new_user = try_create_user(ctx, username, password, email)

    return new_user


def try_create_user(
    ctx: ContextValues,
    username: Optional[str],
    password: Optional[str],
    email: Optional[str],
):
    """
    Runs checks on provided values, creates new user and adds it to database.
    Throws exception otherwise.
    """

    if not username or not password or not email:
        raise ValueError("Provide username, password & email")

    if not username == sanitize_for_url(username):
        raise RYLBadUsername("Username contains special symbols")

    if not string_sanity_check(username):
        raise RYLBadUsername("Username contains inappropriate symbols")

    if not password_sanity_check(password):
        raise RYLBadPassword("Password is too weak")

    new_user = User(
        username=username,
        password=password,
        email=email,
    )

    ctx.set()
    db.session.add(new_user)
    db.session.commit()

    return new_user
