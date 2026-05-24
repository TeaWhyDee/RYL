from datetime import date
from typing import List, Optional

import marshmallow
from apiflask.fields import Nested
from marshmallow import Schema, post_load
from marshmallow.fields import Boolean, Date, Enum, Integer, String

from app.db.models.credit import LevelCreatorRole
from app.db.models.level import (
    GDVersion,
    LevelDifficulty,
    LevelLength,
    LevelRating,
)


class SongDataSchema(Schema):
    # song
    song_name = String()
    song_ngid = Integer()
    # artist
    song_artist_names = marshmallow.fields.List(
        String, required=False, allow_none=True
    )
    song_artist_ngids = marshmallow.fields.List(
        String, required=False, allow_none=True
    )


class LevelDataSchema(Schema):
    name = String()
    publisher = String()
    publisher_gdid = Integer()

    gdid = Integer()
    gd_version = Enum(enum=GDVersion)
    gd_version_original = Enum(GDVersion)

    gd_downloads = Integer()
    gd_likes = Integer()
    gd_difficulty = Enum(LevelDifficulty)
    gd_rating = Enum(LevelRating)
    gd_length = Enum(LevelLength, required=False, allow_none=True)
    gd_length_seconds = Integer(required=False, allow_none=True)
    gd_is_twoplayer = Boolean()
    gd_is_platformer = Boolean()
    # song_data = Nested(SongDataSchema, many=True)

    # TODO

    date_published = Date(required=False, allow_none=True)
    video_url = String(required=False, allow_none=True)
    thumbnail_url = String(required=False, allow_none=True)

    @post_load
    def make_level(self, data, **kwargs):
        return LevelData(**data)


class CreditData:
    # creator credit
    creator_gdid: int
    creator_name: str
    creator_role: Optional[LevelCreatorRole]

    def __init__(
        self,
        creator_gdid: int,
        creator_name: str,
        creator_role: LevelCreatorRole,
    ):
        self.creator_gdid = creator_gdid
        self.creator_name = creator_name
        self.creator_role = creator_role

    def __str__(self):
        attrs = vars(self)
        lines = [f"{k}={v}" for k, v in attrs.items()]
        return "{\n  " + "\n  ".join("  " + line for line in lines) + "\n  }"


class SongData:
    song_ngid: Optional[int]
    song_name: str
    song_artist_ngids: Optional[List[int]]
    song_artist_names: List[str]

    def __init__(
        self,
        song_name: str,
        song_artist_names: List[str],
        song_ngid: Optional[int] = None,
        song_artist_ngids: Optional[List[int]] = None,
    ) -> None:
        self.song_ngid = song_ngid
        self.song_name = song_name
        self.song_artist_ngids = song_artist_ngids
        self.song_artist_names = song_artist_names

    def __str__(self):
        attrs = vars(self)
        lines = [f"{k}={v}" for k, v in attrs.items()]
        return "{\n  " + "\n  ".join("  " + line for line in lines) + "\n  }"


class LevelData:
    gdid: int
    name: Optional[str] = None
    publisher: Optional[str] = None
    publisher_gdid: Optional[int] = None
    gd_version: Optional[GDVersion] = None
    gd_version_original: Optional[GDVersion] = None
    #
    gd_downloads: Optional[int] = None
    gd_likes: Optional[int] = None
    gd_difficulty: Optional[LevelDifficulty] = None
    gd_rating: Optional[LevelRating] = None
    gd_length: Optional[LevelLength] = None
    gd_length_seconds: Optional[int] = None
    gd_is_twoplayer: Optional[bool] = None
    gd_is_platformer: Optional[bool] = False
    #
    song_data: Optional[SongData] = None
    date_published: Optional[date] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    #
    creator_credits: Optional[List[CreditData]] = None

    # def merge(self, other):
    #     for key, value in vars(other).items():
    #         if value is not None and hasattr(self, key):
    #             setattr(self, key, value)
    #
    #     return self

    def merge(self, other):
        for key, value in vars(other).items():
            if value is not None and hasattr(self, key):
                existing = getattr(self, key)
                # Concatenate if both are lists
                if isinstance(existing, list) and isinstance(value, list):
                    setattr(self, key, existing + value)
                else:
                    setattr(self, key, value)
        return self

    def __init__(
        self,
        gdid: int,
        name: Optional[str] = None,
        publisher: Optional[str] = None,
        publisher_gdid: Optional[int] = None,
        gd_version: Optional[GDVersion] = None,
        gd_version_original: Optional[GDVersion] = None,
        # gd
        gd_downloads: Optional[int] = None,
        gd_likes: Optional[int] = None,
        gd_difficulty: Optional[LevelDifficulty] = None,
        gd_rating: Optional[LevelRating] = None,
        gd_length: Optional[LevelLength] = None,
        gd_is_twoplayer: Optional[bool] = None,
        # song
        song_data: Optional[SongData] = None,
        #
        gd_is_platformer: Optional[bool] = False,
        gd_length_seconds: Optional[int] = None,
        date_published: Optional[date] = None,
        thumbnail_url: Optional[str] = None,
        video_url: Optional[str] = None,
        #
        creator_credits: Optional[List[CreditData]] = None,
    ):
        self.gdid = gdid
        self.name = name
        self.publisher = publisher
        self.publisher_gdid = publisher_gdid
        self.gd_version = gd_version
        self.gd_version_original = gd_version_original
        # GD
        self.gd_downloads = gd_downloads
        self.gd_likes = gd_likes
        self.gd_difficulty = gd_difficulty
        self.gd_rating = gd_rating
        self.gd_length = gd_length
        self.gd_is_twoplayer = gd_is_twoplayer
        self.gd_length_seconds = gd_length_seconds
        # Song
        self.song_data = song_data
        #
        self.gd_is_platformer = gd_is_platformer
        self.date_published = date_published
        self.thumbnail_url = thumbnail_url
        self.video_url = video_url
        #
        self.creator_credits = creator_credits

    def __str__(self):
        attrs = vars(self)
        lines = [f"{k}={v}" for k, v in attrs.items()]
        return "{\n" + "\n".join("  " + line for line in lines) + "\n}"
