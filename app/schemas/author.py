# author.py
# Main Authors of levels.
# Author: Creator | Team

from apiflask import Schema
from apiflask.fields import Integer, Nested

from app.db.models.author import LevelAuthorCreator, LevelAuthorTeam
from app.schemas.creator import CreatorOut, TeamOut


#
# ===== Creators =====
#
class AuthorCreatorIn(Schema):
    class Meta:
        model = LevelAuthorCreator

    level_id = Integer()
    creator_id = Integer()


class AuthorCreatorOut(Schema):
    class Meta:
        model = LevelAuthorCreator

    id = Integer()
    level_id = Integer()
    creator_id = Integer()


class AuthorCreatorOutExtra(Schema):
    class Meta:
        model = LevelAuthorCreator
        include_relationships = True

    id = Integer()
    creator = Nested(CreatorOut)


#
# ===== Teams =====
#
class AuthorTeamIn(Schema):
    class Meta:
        model = LevelAuthorTeam

    level_id = Integer()
    team_id = Integer()


class AuthorTeamOut(Schema):
    class Meta:
        model = LevelAuthorTeam

    id = Integer()
    level_id = Integer()
    team_id = Integer()


class AuthorTeamOutExtra(Schema):
    class Meta:
        model = LevelAuthorTeam
        include_relationships = True

    id = Integer()
    team = Nested(TeamOut)
