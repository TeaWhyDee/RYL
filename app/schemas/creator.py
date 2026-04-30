from apiflask.fields import Integer, Nested, String

from app.schemas import RYLInSchema, RYLOutSchema

# from app.db.models.creator import Creator, GD_Account, Team

# from app.schemas.level import LevelOut


class CreatorIn(RYLInSchema):
    name = String()


class CreatorOut(RYLOutSchema):
    id = Integer()
    display_name = String()
    url_name = String()
    about = String()
    clan = String()


class CreatorOutExtra(RYLOutSchema):
    id = Integer()
    display_name = String()
    url_name = String()
    about = String()
    clan = String()
    # Level schema passed as string to avoid circular importing
    levels = Nested("LevelOut", many=True)
