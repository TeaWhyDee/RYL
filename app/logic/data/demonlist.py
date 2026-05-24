import json

from app.logic.data.level_data import CreditData, LevelData


def get_demonlist_levels():
    assert False

    with open("sample_data/demonlist_listed_all.json") as file:
        data = json.load(file)
        sorted_data = sorted(data, key=lambda x: x["position"])

        for level_data in sorted_data:
            level_gdid = level_data["level_id"]
            level_name = level_data["name"]
            level_publisher = level_data["publisher"]["name"]
            _ = level_data["video"]
            _ = level_data["thumbnail"]
            level_verifier = level_data["verifier"]["name"]

            LevelData(
                gdid=level_gdid,
                name=level_name,
                creator_credits=CreditData(),
            )

            return level
