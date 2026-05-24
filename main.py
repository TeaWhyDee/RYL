import csv
import json
import os
import re
import time
from typing import List

import jsonpickle

from app.db.models.credit import LevelCreatorRole
from app.db.models.level import LevelDifficulty, LevelRating
from app.logic.data.all_rated import get_all_rated_levels
from app.logic.data.level_data import CreditData, LevelData, LevelDataSchema
from app.logic.data.retreive_data import (
    augment_level,
    load_json_levels,
    retreive_gdhistory,
)


def test():
    lvl1 = LevelData(
        1, creator_credits=[CreditData(1, "a", LevelCreatorRole.verifier)]
    )

    lvl2 = LevelData(
        1, creator_credits=[CreditData(2, "b", LevelCreatorRole.fx)]
    )

    print(lvl1.merge(lvl2))


def enhance_levels(levels: List[LevelData]):
    levels_ar = get_all_rated_levels("./sample_data/all_rated.csv")

    levels_out = []
    for i, level in enumerate(levels):
        # level = augment_level(level, query_gda_date=True, query_thumbnail=True)

        if level.gdid in levels_ar:
            level = level.merge(levels_ar[level.gdid])

        level_schema = LevelDataSchema()

        print(f"#{i}", flush=True)
        print(level_schema.dumps(level, indent=2))

        levels_out.append(level_schema.dump(level))

    output = json.dumps(levels_out, indent=2)

    with open("sample_data/gdh/processed_gdh500_.json", "w") as file:
        file.write(output)


if __name__ == "__main__":
    # levels_gdh: List[LevelData] = retreive_gdhistory(use_cache=True, limit=500)
    levels_gdh: List[LevelData] = load_json_levels(
        "sample_data/gdh/processed_gdh500.json"
    )
    enhance_levels(levels_gdh)
