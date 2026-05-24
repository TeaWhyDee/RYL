from typing import Optional

from app import db
from app.db.models.level import GDVersion, LevelDifficulty, LevelRating
from app.db.models.level_upload import LevelUpload
from app.utility.context import ContextValues
from app.utility.exceptions import RYLAlreadyExists


def get_level_upload(id: int):
    level_upload = LevelUpload.query.filter_by(id=id).one_or_none()
    return level_upload


def try_add_level_upload(
    ctx: ContextValues,
    gdid: int,
    gd_title: str,
    gd_server_id: int,
    song_ng_id: int,
    gd_account_id: int,
    gd_rating: LevelRating,
    gd_difficulty: LevelDifficulty,
    level_id: int,
    gd_cache_likes: Optional[int],
    note: Optional[str] = None,
    gd_version_original: Optional[GDVersion] = None,
    gd_version_last: Optional[GDVersion] = None,
):
    new_upload = LevelUpload(
        gdid=gdid,
        gd_title=gd_title,
        gd_server_id=gd_server_id,
        song_ng_id=song_ng_id,
        gd_account_id=gd_account_id,
        gd_rating=gd_rating,
        gd_difficulty=gd_difficulty,
        level_id=level_id,
        note=note,
        gd_cache_likes=gd_cache_likes,
        gd_version_original=gd_version_original,
        gd_version_last=gd_version_last,
    )

    ctx.set()
    db.session.add(new_upload)
    db.session.commit()

    return new_upload
