import json

import requests


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


if __name__ == "__main__":
    retreive_aredl()
    # import_demonlist_json()
    # retreive_demonlist()
