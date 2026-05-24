from apiflask.fields import Integer, String

from app.schemas import RYLOut


class SongOut(RYLOut):
    id = Integer()
    display_name = String()
    url_name = String()
    about = String()
    clan = String()
