import json

from sqlalchemy_declarative_extensions.audit import set_context_values

from app.db.database import db
from app.db.models.creator import Creator
from app.db.models.credit import LevelCreatorRole, LevelCredit
from app.db.models.level import Level, LevelLength, LevelRating, LevelType
from app.db.services.creator import add_or_get_creator
from app.db.services.credit import add_or_get_credit
from app.db.services.level import add_or_get_level
from app.utility.context import ContextValues


def import_demonlist_json():
    context_values = ContextValues(note="demonlist")

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

            lvl = Level.query.filter_by(GD_id=level_id).one_or_none()
            if lvl:
                continue

            level = add_or_get_level(
                context_values,
                level_id,
                level_name,
                level_publisher,
                LevelType.level,
                LevelLength.long,
                LevelRating.featured,
            )

            creator = add_or_get_creator(context_values, level_publisher)

            verifier = add_or_get_creator(context_values, level_verifier)
            _ = add_or_get_credit(
                context_values, level.id, verifier.id, LevelCreatorRole.verifier
            )

            return


def import_aredl_json():
    set_context_values(db.session, user_id=1, note="aredl")
    pass
