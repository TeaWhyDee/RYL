import re

from app.db.database import Base

"""
String sanitization and such.
"""

URI_STRICT = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._"
URI_RESERVED = ":/?#[]@!$&'()*+,;="

URI_MATCH_STRICT = r"^[a-zA-Z0-9\-._]+$"
URI_REPLACE_STRICT = r"[^a-zA-Z0-9\-._~]"


def is_valid_string(s):
    return bool(re.match(URI_MATCH_STRICT, s))


def get_url_name(display_name: str, query) -> str:
    """
    based on display_name string and query for the model,
    returns a unique url_name.
    """
    sanitized = sanitize_for_url(display_name)
    url_name = sanitized

    # if already exists, add suffix
    offset = 2
    while query.filter_by(url_name=url_name).one_or_none():
        url_name = f"{sanitized}-{offset}"
        offset += 1

    return url_name


def sanitize_for_url(string: str) -> str:
    """
    Lowers all characters
    Repalces ' ' (space) with '-'
    Replaces all special characters with '_' except for '.', '_', '-'
    """
    sanitized = string.replace(" ", "-").lower()
    sanitized = re.sub(URI_REPLACE_STRICT, "_", sanitized)

    return sanitized


def string_sanity_check(string: str) -> bool:
    """
    Meant for user content.
    Filter out inappropriate strings.
    Returns False if string contains questionable symbols.
    """

    # TODO
    if "fuck" in string or string == "":
        return False

    return True


def password_sanity_check(pwd: str) -> bool:
    """
    Filter out bad password.
    Returns False if password is weak.
    """

    if pwd == "password" or pwd == "12345678" or len(pwd) < 8:
        return False

    return True
