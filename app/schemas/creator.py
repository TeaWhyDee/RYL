from apiflask import APIFlask, Schema
from apiflask.fields import Boolean, Enum, Integer, Nested, String

from app.db.models.creator import Creator, GD_Account, Team

# from app.schemas.level import LevelOut


class CreatorIn(Schema):
    name = String()


class CreatorOut(Schema):
    id = Integer()
    display_name = String()
    url_name = String()
    about = String()
    clan = String()


class CreatorOutExtra(Schema):
    id = Integer()
    display_name = String()
    url_name = String()
    about = String()
    clan = String()
    # Level schema passed as string to avoid circular importing
    levels = Nested("LevelOut", many=True)
