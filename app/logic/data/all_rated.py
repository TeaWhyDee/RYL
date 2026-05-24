import csv
import re

from app.db.models.level import GDVersion, LevelRating
from app.logic.data.level_data import LevelData, SongData

AR_RATING_MAPPING = {
    "✔": LevelRating.rated,
    "✨": LevelRating.featured,
    "🔥": LevelRating.epic,
    "🌸": LevelRating.legendary,
    "💎": LevelRating.mythic,
}

AR_VER_MAPPING = {
    "1.0": GDVersion.ver10,
    "1.1": GDVersion.ver11,
    "1.2": GDVersion.ver12,
    "1.3": GDVersion.ver13,
    "1.4": GDVersion.ver14,
    "1.5": GDVersion.ver15,
    "1.6": GDVersion.ver16,
    "1.7": GDVersion.ver17,
    "1.8": GDVersion.ver18,
    "1.9": GDVersion.ver19,
    "2.0": GDVersion.ver20,
    "2.1": GDVersion.ver21,
    "2.2": GDVersion.ver22,
}


def get_all_rated_levels(file_path) -> dict:
    """
    @return dict of gdid: LevelData pairs.
    """
    levels = {}

    with open(file_path, "r") as file:
        # lines = [x.split(",") for x in file.readlines()]
        reader = csv.DictReader(file)

        for i, line in enumerate(reader):
            gdid = int(line["Level ID"])
            url = line["URL"]  # 1
            version = AR_VER_MAPPING[line["Version"]]  # 08
            rating = AR_RATING_MAPPING[line["Rating"]]  # 12
            # length
            length = line["Length"]  # 9
            if length == "NA":
                length = None
            else:
                length = sum(
                    int(x) * 60**i
                    for i, x in enumerate(reversed(length.split(":")))
                )
            # song
            song_ngid = line["Song ID(s)"]  # 8
            if "Official" in song_ngid:
                song_ngid = re.findall(r"\d+", song_ngid)[0]
            elif "Multiple" in song_ngid:
                song_ngid = None
            else:
                song_ngid = int(song_ngid)

            song_name = line["Song(s)"]
            song_artist_names = line["Song Artist(s)"].split(", ")
            if "Multiple" in song_name:
                song_name = None
                song_artist_names = None

            song_data = (
                SongData(
                    song_name=song_name,
                    song_ngid=song_ngid,
                    song_artist_names=song_artist_names,
                )
                if song_name and song_artist_names
                else None
            )

            # is_platformer
            is_platformer = "🌙" in line["Reward"]

            levels[gdid] = LevelData(
                gdid=gdid,
                gd_version_original=version,
                video_url=url,
                gd_rating=rating,
                gd_length_seconds=length,
                gd_is_platformer=is_platformer,
                #
                song_data=song_data,
            )

    return levels
