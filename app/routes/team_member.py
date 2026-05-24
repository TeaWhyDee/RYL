from apiflask import (
    APIBlueprint,
    PaginationSchema,
    Schema,
    abort,
    pagination_builder,
)
from apiflask.fields import Enum, Integer, List, Nested
from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import current_user

from app.db.database import db
from app.db.models.team import Team
from app.db.models.team_member import TeamMember, TeamRole
from app.db.models.user import UserRole
from app.db.services.team_member import try_add_team_member
from app.routes import PageSchema
from app.schemas import RYLContentIn
from app.schemas.team_member import (
    TeamMemberIn,
    TeamMemberOut,
    TeamMemberOutExtra,
    TeamMemberPatch,
)
from app.utility.auth import ryl_auth
from app.utility.context import ContextValues
from app.utility.crud_auth import CRUD_AUTH_ROLES
from app.utility.database import check_model_difference
from app.utility.error import RYLUpdateNoChange
from app.utility.exceptions import RYLAlreadyExists

app_team_member = APIBlueprint("team_member", __name__)


class TeamMembersQuery(PageSchema):
    team_id = Integer(required=False)
    creator_id = Integer(required=False)
    role = Enum(TeamRole, required=False)


class TeamMembersPage(Schema):
    # members = List(Nested(TeamMemberOut))
    members = List(Nested(TeamMemberOutExtra))
    pagination = Nested(PaginationSchema)


class TeamMembersView(MethodView):
    @app_team_member.input(TeamMembersQuery, location="query")
    @app_team_member.output(TeamMembersPage, status_code=200)
    @app_team_member.doc(
        "List team members or search/filter by team, creator, or role",
        responses=[200],
    )
    def get(self, query_data):
        """
        Search team members.
        Filters:
        - team_id (optional)
        - creator_id (optional)
        - role (optional)
        Returns paginated list with pagination metadata.
        """
        base_query = TeamMember.query

        # Apply filters if provided
        if "team_id" in query_data:
            base_query = base_query.filter(
                TeamMember.team_id == query_data["team_id"]
            )

        if "creator_id" in query_data:
            base_query = base_query.filter(
                TeamMember.creator_id == query_data["creator_id"]
            )

        if "role" in query_data:
            base_query = base_query.filter(
                TeamMember.role == query_data["role"]
            )

        pagination = base_query.paginate(
            page=query_data["page"], per_page=query_data["per_page"]
        )

        members = pagination.items
        return {
            "members": members,
            "pagination": pagination_builder(pagination),
        }

    @app_team_member.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["team_member"].create
    )
    @app_team_member.input(TeamMemberIn, location="json")
    @app_team_member.output(TeamMemberOut, status_code=201)
    @app_team_member.doc("Add a team member", responses=[409])
    def post(self, json_data):
        """
        Add a new team member.
        """

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )

            new_member = try_add_team_member(
                ctx=ctx,
                team_id=int(json_data["team_id"]),
                creator_id=int(json_data["creator_id"]),
                role=TeamRole(json_data["role"]),
                date_joined=json_data.get("date_joined"),
                date_left=json_data.get("date_left"),
            )

            return new_member, 201

        except RYLAlreadyExists as e:
            current_app.logger.warning(e)
            abort(409, message=e.message)

        except Exception as e:
            current_app.logger.warning(e)
            abort(500)


class TeamMemberView(MethodView):
    @app_team_member.output(TeamMemberOut, status_code=200)
    @app_team_member.doc("Get a specific team member", responses=[404])
    def get(self, team_member_id):
        """
        Get details of a specific team member by ID.
        """
        member = TeamMember.query.filter_by(id=team_member_id).one_or_none()

        if not member:
            abort(404)

        return member

    @app_team_member.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["team_member"].update
    )
    @app_team_member.input(TeamMemberPatch(partial=True))
    @app_team_member.output(TeamMemberOut, status_code=200)
    @app_team_member.doc("Update a team member", responses=[403, 404, 500])
    def patch(self, team_member_id, json_data):
        """
        Update a team member with JSON data.
        """
        current_app.logger.info(
            f"Request: Patch team_member({team_member_id}): {json_data}"
        )

        query = TeamMember.query.filter_by(id=team_member_id)
        member: TeamMember = query.one_or_none()
        if not member:
            abort(404)

        if not check_model_difference(member, json_data):
            raise RYLUpdateNoChange()

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )
            ctx.set()

            query.update(json_data)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)

        return member

    @app_team_member.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["team_member"].delete
    )
    @app_team_member.input(RYLContentIn(partial=True))
    @app_team_member.output({}, status_code=204)
    @app_team_member.doc("Delete a team member", responses=[204, 401, 403, 404])
    def delete(self, team_member_id, json_data):
        current_app.logger.info(
            f"Request: Delete team member: {team_member_id}"
        )

        team_member = TeamMember.query.filter_by(
            id=team_member_id
        ).one_or_none()

        if not team_member:
            abort(404)

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note")
            )
            ctx.set()

            db.session.delete(team_member)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


app_team_member.add_url_rule(
    "/v1/team_members", view_func=TeamMembersView.as_view("teams")
)
app_team_member.add_url_rule(
    "/v1/team_member/<int:team_member_id>",
    view_func=TeamMemberView.as_view("team"),
)
