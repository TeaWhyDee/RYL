from apiflask.fields import Integer, Nested

from app.schemas import RYLContentIn, RYLOut
from app.schemas.genre import GenreOut


class LevelGenreIn(RYLContentIn):
    level_id = Integer(required=True)
    genre_id = Integer(required=True)


class LevelGenrePatch(RYLContentIn):
    pass


class LevelGenreOutMin(RYLOut):
    level_id = Integer()
    genre_id = Integer()


class LevelGenreOut(LevelGenreOutMin):
    pass


class LevelGenreOutExtra(RYLOut):
    genre = Nested(GenreOut)
