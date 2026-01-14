from apiflask import APIFlask, Schema
from apiflask.fields import Boolean, Date, Enum, Integer, Nested, String

from app.db.models.creator import Creator, GD_Account, Team


#
# ===== Creator =====
#
class CreatorIn(Schema):
    name = String()


class CreatorOut(Schema):
    id = Integer()
    display_name = String()
    url_name = String()
    clan = String()
    about = String()


class CreatorOutExtra(Schema):
    id = Integer()
    display_name = String()
    url_name = String()
    clan = String()
    about = String()
    level_authorships = Nested("LevelOut", many=True)
    team_memberships = Nested("TeamMemberOutTeamExtra", many=True)
    # credits = Nested("LevelOut", many=True)


#
# ===== Team =====
#
class TeamIn(Schema):
    name = String()


class TeamOut(Schema):
    id = Integer()
    display_name = String()
    url_name = String()
    about = String()


class TeamOutExtra(Schema):
    id = Integer()
    display_name = String()
    url_name = String()
    about = String()
    level_authorships = Nested("LevelOut", many=True)
    memberships = Nested("TeamMemberCreatorExtra", many=True)


#
# ===== Team Member =====
#
class TeamMemberIn(Schema):
    creator_id = Integer()
    team_id = Integer()


class TeamMemberOut(Schema):
    id = Integer()
    creator_id = Integer()
    team_id = Integer()
    membership_start = Date()
    membership_end = Date()
    is_owner = Boolean()


class TeamMemberTeamExtra(Schema):
    id = Integer()
    team = Nested(TeamOut)
    membership_start = Date()
    membership_end = Date()
    is_owner = Boolean()


class TeamMemberCreatorExtra(Schema):
    id = Integer()
    creator = Nested(CreatorOut)
    membership_start = Date()
    membership_end = Date()
    is_owner = Boolean()
