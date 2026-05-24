import json
from datetime import date
from typing import List, Optional

import jsonpickle
import requests
from googleapiclient.http import HttpError
from marshmallow import Schema

from app.config.dev import YT_API_KEY
from app.db.models.level import (
    GDVersion,
    LevelDifficulty,
    LevelLength,
    LevelRating,
)
from app.logic.data.level_data import LevelData, LevelDataSchema, SongData

# Example:
# [
#   {
#     "name": "Thinking Space II",
#     "publisher": "CairoX",
#     "GD_id": 119544028,
#     "description": "An official sequel to Thinking Space, and currently the hardest rated level in the game. Unlike the original, its decoration is in a glow design style, but it's more similar in gameplay as it has several gameplay references to the original and is also extremely end carried. (aredl.net)",
#     "two_player": false,
#     "video_url":  "https://www.youtube.com/watch?v=CELNmHwln_c",
#     "creators": [
#         {
#             "creator": "CairoX"
#         }
#     ],
#     "credits": [
#         {
#             "name": "Zoink",
#             "role": "verifier"
#         },
# ...


def retreive_demonlist():
    # endpoint = "https://pointercrate.com/api/v2/demons/listed/?limit=100&after=100"
    endpoint = "https://pointercrate.com/api/v2/demons/listed/"

    combined_data = []
    for page in range(1, 10):
        limit = 100
        after = page * 100
        endpoint_page = f"{endpoint}?limit={limit}&after={after}"
        response = requests.get(endpoint_page)

        data = json.loads(response.text)
        combined_data.extend(data)

    print(combined_data)
    with open("sample_data/demonlist_combined.json", "w") as file:
        json.dump(combined_data, file, indent=4)


def retreive_aredl():
    endpoint_levels = "https://api.aredl.net/v2/api/aredl/levels"
    response_levels = requests.get(endpoint_levels)

    data = json.loads(response_levels.text)
    # print(data, flush=True)

    levels = []

    i = 20
    for level in data:
        if i < 1:
            continue
        i -= 1

        uuid = level["id"]
        endpoint_level = f"https://api.aredl.net/v2/api/aredl/levels/{uuid}"
        response_level = requests.get(endpoint_level)
        data_level = json.loads(response_level.text)

        level_name = data_level["name"]
        level_id = data_level["level_id"]
        description = data_level["description"] + " (aredl.net)"
        tags = data_level["tags"]
        two_player = data_level["two_player"]

        publisher = data_level["publisher"]["global_name"]
        verifier = data_level["verifications"][0]["submitted_by"]["global_name"]
        video_url = data_level["verifications"][0]["video_url"]

        endpoint_creators = (
            f"https://api.aredl.net/v2/api/aredl/levels/{uuid}/creators"
        )
        response_creators = requests.get(endpoint_creators)
        data_creators = json.loads(response_creators.text)

        level_credits = []
        level_credits.append({"name": verifier, "role": "verifier"})
        for data_creator in data_creators:
            level_credits.append(
                {"name": data_creator["global_name"], "role": "collaborator"}
            )

        edel_enjoyment = (
            data_level["edel_enjoyment"]
            if not data_level["is_edel_pending"]
            else None
        )

        level = {
            "name": level_name,
            "publisher": publisher,
            "GD_id": level_id,
            "description": description,
            "two_player": two_player,
            "creators": [{"creator": publisher}],
            "credits": level_credits,
            "video_url": video_url,
            "edel_enjoyment": edel_enjoyment,
            "song": data_level["song"],
            "tags": data_level["tags"],
        }

        print(level, flush=True)

        levels.append(level)

    # print(levels)
    with open("sample_data/aredl_combined.json", "w") as file:
        json.dump(levels, file, indent=4)


GDH_DIFF_MAPPING = {
    1: LevelDifficulty.auto,
    2: LevelDifficulty.easy,
    3: LevelDifficulty.normal,
    4: LevelDifficulty.hard,
    5: LevelDifficulty.harder,
    6: LevelDifficulty.insane,
    # 7: LevelDifficulty.demon
    8: LevelDifficulty.easy_demon,
    9: LevelDifficulty.medium_demon,
    10: LevelDifficulty.hard_demon,
    11: LevelDifficulty.insane_demon,
    12: LevelDifficulty.extreme_demon,
}

GDH_LEN_MAPPING = {
    0: LevelLength.tiny,
    1: LevelLength.short,
    2: LevelLength.medium,
    3: LevelLength.long,
    4: LevelLength.XL,
}

GDH_VER_MAPPING = {
    0: GDVersion.ver10,
    1: GDVersion.ver10,
    2: GDVersion.ver11,
    3: GDVersion.ver12,
    4: GDVersion.ver13,
    5: GDVersion.ver14,
    6: GDVersion.ver15,
    7: GDVersion.ver16,
    10: GDVersion.ver17,
    11: GDVersion.ver18,
    #
    18: GDVersion.ver18,
    19: GDVersion.ver19,
    20: GDVersion.ver20,
    21: GDVersion.ver21,
    22: GDVersion.ver22,
}


def load_json_levels(file_name: str) -> List[LevelData]:
    with open(file_name, "r") as file:
        data = json.loads(file.read())

    levels = []

    for i, level in enumerate(data):
        schema = LevelDataSchema()
        level_data = schema.load(data=level)

        levels.append(level_data)

    return levels


def retreive_gdhistory(use_cache=True, limit=10):
    data = {}

    if not use_cache:
        url = "https://history.geometrydash.eu/api/v1/search/level/advanced/"
        params = {"sort": "cache_likes:desc", "limit": limit}

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()["hits"]

            with open(f"sample_data/gdh/gdhistory{limit}.json", "w") as file:
                json.dump(data, file, indent=2)
        else:
            print(f"Request failed with status code: {response.status_code}")

    else:  # use cache
        with open(f"sample_data/gdh/gdhistory{limit}.json", "r") as file:
            # print(file)
            data = json.loads(file.read())

    levels = {}

    for i, level in enumerate(data):
        if level["is_deleted"]:
            continue

        level_is_platformer = False
        if level["cache_length"] == 5:
            level_is_platformer = True
            level_length = None
        else:
            level_length = GDH_LEN_MAPPING[level["cache_length"]]

        # print(level)
        level_name = level["cache_level_name"]
        level_gdid = level["online_id"]
        level_publisher = level["cache_username"]
        level_publisher_gdid = level["cache_user_id"]

        level_downloads = level["cache_downloads"]
        level_likes = level["cache_likes"]
        level_diff = GDH_DIFF_MAPPING[level["cache_filter_difficulty"]]
        level_gd_version = GDH_VER_MAPPING[level["cache_game_version"]]
        level_gd_version_original = GDH_VER_MAPPING[
            level["cache_min_game_version"]
        ]
        level_is_twoplayer = level["cache_two_player"]
        level_song_ngid = level["cache_song_id"]
        level_song_artist_ngid = level["cache_song_artist_id"]
        # level_ = level["cache_min_game_version"]

        if level["cache_epic"] != 0:
            level_rating = LevelRating.epic
        elif level["cache_featured"] != 0:
            level_rating = LevelRating.featured
        elif level["cache_stars"] != 0:
            level_rating = LevelRating.rated
        else:
            level_rating = LevelRating.unrated

        level = LevelData(
            name=level_name,
            publisher=level_publisher,
            publisher_gdid=level_publisher_gdid,
            gdid=level_gdid,
            gd_version=level_gd_version,
            gd_version_original=level_gd_version_original,
            # gd
            gd_downloads=level_downloads,
            gd_likes=level_likes,
            gd_difficulty=level_diff,
            gd_rating=level_rating,
            gd_length=level_length,
            gd_is_twoplayer=level_is_twoplayer,
            gd_is_platformer=level_is_platformer,
            # song
        )

        levels[level_gdid] = level

        if i > limit:
            break

    return levels


def lookup_gdh_date(level_id: int) -> Optional[date]:
    url = f"https://history.geometrydash.eu/api/v1/date/level/{level_id}/?mode=brief"

    data = {}
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        date_str = data["approx"]["estimation"]
        level_date = date.strptime(date_str[0:10], "%Y-%m-%d")

        return level_date

    else:
        return None


def get_level_video_gdarchive(
    level_name: str, creator_name: Optional[str] = None
) -> Optional[str]:
    channel_id = "UC7AyoTC9NJarSYleR1_ZwJw"

    return lookup_level_video(channel_id, level_name, creator_name)


def lookup_level_video(
    channel_id: str, level_name: str, creator_name: Optional[str] = None
) -> Optional[str]:
    from googleapiclient.discovery import build

    print(level_name, creator_name)

    youtube = build("youtube", "v3", developerKey=YT_API_KEY)

    search_string = level_name
    if creator_name:
        search_string = f"{level_name} by {creator_name}"

    print(f'looking up "{search_string}"')

    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=1,
        q=search_string,
        type="video",
    )

    response = request.execute()
    try:

        video_id = response["items"][0]["id"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        # print(video_url)

        return video_url

    except HttpError as e:
        print("==================")
        print(f"HTTP_ERROR: {e}")
        print("==================")
    except:
        return None


def augment_level(
    level: LevelData,
    query_gda_date: bool = False,
    query_yt: bool = False,
    query_thumbnail: bool = False,
) -> LevelData:

    level_name = level.name or ""
    creator_name = level.publisher

    if query_yt:
        url = get_level_video_gdarchive(
            level_name=level_name, creator_name=creator_name
        )
        if url:
            level.video_url = url

    if query_gda_date:
        date_approx = lookup_gdh_date(level.gdid)
        if date_approx:
            level.date_published = date_approx

    if query_thumbnail:
        thumb_url = f"https://levelthumbs.prevter.me/thumbnail/{level.gdid}"

        thumb_available = requests.head(thumb_url).ok
        if thumb_available:
            level.thumbnail_url = thumb_url

    return level


if __name__ == "__main__":
    levels = retreive_gdhistory()
    # retreive_aredl()
    # retreive_demonlist()
