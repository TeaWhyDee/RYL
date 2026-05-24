import uuid
from unittest.mock import patch

import pytest

from app.db.models.user import User, UserRole
from app.db.services.user import try_create_user
from app.utility.context import ContextValues
from app.utility.exceptions import RYLBadPassword, RYLBadUsername


def test_user_creation(session):
    user = User(username="Yep!!", password="thiscodewas", email="test@test.com")
    session.add(user)
    session.commit()

    assert user.id is not None
    assert user.username == "yep__"
    assert user.display_name == "Yep!!"
    assert user.email == "test@test.com"
    assert user.is_banned is False
    assert user.is_deleted is False
    assert user.user_role == UserRole.normal

    assert "yep__" in repr(user)


def test_bad_user_creation(ctx_mock, db_patch):
    # bad password
    bad_passwords = ["p", "password", "12345678"]
    for bad_pwd in bad_passwords:
        with pytest.raises(RYLBadPassword):
            try_create_user(ctx_mock, "name", bad_pwd, email="t@t.com")

    # bad username
    bad_usernames = ["", "fuck", "name/", " name", "name ", "name&%"]
    for bad_name in bad_usernames:
        with pytest.raises(RYLBadUsername):
            try_create_user(ctx_mock, bad_name, "asd09f87", email="t@t.com")

    # try_create_user(ctx_mock, "name", "asd09f8asd7", email="test@test.com")


def test_password_is_hashed():
    user = User(username="bob", password="secret123", email="b@example.com")
    assert user.password != "secret123"  # hashing occurred


def test_check_password():
    user = User(username="bob", password="secret123", email="c@example.com")
    assert user.check_password("secret123")
    assert not user.check_password("wrong")


def test_user_role_change(session):
    user = User(username="bob", password="pw", email="d@example.com")
    user.user_role_change(UserRole.admin)

    session.add(user)
    session.commit()
    session.refresh(user)

    assert user.user_role == UserRole.admin
