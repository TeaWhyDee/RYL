from apiflask.fields import Integer, String

from app.schemas import RYLOutSchema


class SongOut(RYLOutSchema):
    id = Integer()
    display_name = String()
    url_name = String()
    about = String()
    clan = String()
