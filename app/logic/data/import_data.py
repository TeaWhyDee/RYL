import json
from typing import List

from sqlalchemy_declarative_extensions.audit import set_context_values

from app.db.database import CompletenessStatus, db
from app.db.models.creator import Creator
from app.db.models.credit import LevelCreatorRole, LevelCredit
from app.db.models.gd_account import GDAccount
from app.db.models.level import (
    Level,
    LevelDifficulty,
    LevelLength,
    LevelRating,
    LevelType,
)
from app.db.services.creator import add_or_get_creator, try_add_creator
from app.db.services.credit import find_credit, get_credit, try_add_credit
from app.db.services.gd_account import (
    find_gd_account,
    get_gd_account,
    try_add_gd_account,
)
from app.db.services.level import get_level, try_add_level
from app.db.services.level_authorship import try_add_level_authorship
from app.db.services.level_upload import try_add_level_upload
from app.logic.data.all_rated import get_all_rated_levels
from app.logic.data.retreive_data import LevelData, load_json_levels
from app.utility.context import ContextValues


def import_leveldata(level_data: LevelData, note: str):
    # TODO
    # TODO
    # TODO

    ctx = ContextValues(user_id=1, note=note)

    level_id = LevelData.gdid

    assert LevelData.name

    level = Level.query.filter_by(GD_id=level_id).one_or_none()
    if not level:
        level = try_add_level(
            ctx=ctx,
            level_GD_id=level_id,
            level_name=LevelData.name,
            level_type=LevelType.level,
            # level_publisher=level_publisher,
            # LevelLength=LevelLength.long,
            # LevelRating=LevelRating.featured,
            completeness_status=CompletenessStatus.imported_extra,
        )


def import_demonlist_json():
    ctx = ContextValues(user_id=1, note="demonlist")

    with open("sample_data/demonlist_listed_all.json") as file:
        data = json.load(file)
        sorted_data = sorted(data, key=lambda x: x["position"])

        for level_data in sorted_data:
            level_id = level_data["level_id"]
            level_name = level_data["name"]
            level_publisher = level_data["publisher"]["name"]
            _ = level_data["video"]
            _ = level_data["thumbnail"]
            level_verifier = level_data["verifier"]["name"]

            level = Level.query.filter_by(GD_id=level_id).one_or_none()
            if not level:
                level = try_add_level(
                    ctx=ctx,
                    level_GD_id=level_id,
                    level_name=level_name,
                    level_type=LevelType.level,
                    # level_publisher=level_publisher,
                    # LevelLength=LevelLength.long,
                    # LevelRating=LevelRating.featured,
                    completeness_status=CompletenessStatus.imported_extra,
                )

            creator = add_or_get_creator(
                ctx=ctx,
                creator_name=level_publisher,
                completeness_status=CompletenessStatus.imported_extra,
                description="imported from demonlist",
            )

            verifier = add_or_get_creator(
                ctx=ctx,
                creator_name=level_verifier,
                completeness_status=CompletenessStatus.imported_extra,
                description="imported from demonlist",
            )

            verifier_credit = find_credit(
                level_id=level.id,
                creator_id=verifier.id,
                role=LevelCreatorRole.verifier,
            )
            if not verifier_credit:
                try_add_credit(
                    ctx,
                    level.id,
                    verifier.id,
                    LevelCreatorRole.verifier,
                )

            return level


def add_leveldata_level(level_data: LevelData):
    ctx = ContextValues(user_id=1, note="demonlist")

    if not level_data.name or not (
        level_data.publisher or level_data.publisher_gdid
    ):
        raise Exception

    existing_level = Level.query.filter_by(GD_id=level_data.gdid).one_or_none()
    if existing_level:
        return None

    song_ngid = 0
    if level_data.song_data:
        song_ngid = level_data.song_data.song_ngid or 0

    level = try_add_level(
        ctx,
        completeness_status=CompletenessStatus.imported_extra,
        #
        level_GD_id=level_data.gdid,
        level_name=level_data.name,
        level_type=(
            LevelType.platformer
            if level_data.gd_is_platformer
            else LevelType.level
        ),
        #
        level_length=level_data.gd_length,
        level_length_seconds=level_data.gd_length_seconds,
        level_rating=level_data.gd_rating,
        gd_version=level_data.gd_version,
        gd_difficulty=level_data.gd_difficulty,
        is_two_player=level_data.gd_is_twoplayer or False,
        #
        date_published=level_data.date_published,
        video_url=level_data.video_url,
        thumbnail_url=level_data.thumbnail_url,
    )

    if level_data.publisher and level_data.publisher_gdid:
        creator = add_or_get_creator(
            ctx=ctx,
            creator_name=level_data.publisher,
            completeness_status=CompletenessStatus.imported_extra,
            description="",
        )

        try_add_level_authorship(ctx, level.id, creator.id)

        gd_account = find_gd_account(level_data.publisher_gdid)
        if not gd_account:
            gd_account = try_add_gd_account(
                ctx,
                username=level_data.publisher,
                gd_account_gdid=level_data.publisher_gdid,
                gd_server_id=1,
            )

        try_add_level_upload(
            ctx,
            level_id=level.id,
            #
            gdid=level_data.gdid,
            gd_title=level_data.name,
            gd_server_id=1,
            song_ng_id=song_ngid,
            gd_account_id=gd_account.id,
            gd_rating=level_data.gd_rating or LevelRating.unrated,
            gd_difficulty=level_data.gd_difficulty or LevelDifficulty.na,
            #
            gd_cache_likes=level_data.gd_likes,
            gd_version_original=level_data.gd_version_original,
            gd_version_last=level_data.gd_version,
        )

    # levelupload:
    # likes

    pass


def import_top50_likes():
    levels_ar = get_all_rated_levels("./sample_data/all_rated.csv")

    levels_gdh: List[LevelData] = load_json_levels(
        "sample_data/gdh/gdh50_enhanced.json"
    )

    for i, lvl in enumerate(levels_gdh):
        level_data = lvl.merge(levels_ar[lvl.gdid])

        add_leveldata_level(level_data)


def import_top500_likes():
    levels_gdh: List[LevelData] = load_json_levels(
        "sample_data/gdh/processed_gdh500.json"
    )

    for i, lvl in enumerate(levels_gdh):
        add_leveldata_level(lvl)


def import_aredl_json():
    set_context_values(db.session, user_id=1, note="aredl")
    pass
