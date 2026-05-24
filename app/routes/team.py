from apiflask import (
    APIBlueprint,
    PaginationSchema,
    Schema,
    abort,
    pagination_builder,
)
from apiflask.fields import List, Nested, String
from apiflask.validators import Length
from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import current_user

from app.db.database import CompletenessStatus, db
from app.db.models.team import Team
from app.db.services.team import try_add_team
from app.routes import PageSchema
from app.schemas import RYLContentIn
from app.schemas.team import TeamIn, TeamOut, TeamOutMin, TeamPatch
from app.utility.auth import ryl_auth
from app.utility.context import ContextValues
from app.utility.crud_auth import CRUD_AUTH_ROLES
from app.utility.database import check_model_difference
from app.utility.error import RYLUpdateNoChange
from app.utility.exceptions import RYLAlreadyExists

app_team = APIBlueprint("team", __name__)


class TeamsQuery(PageSchema):
    search_str = String(required=False, validate=Length(1, 50))


class TeamsPage(Schema):
    teams = List(Nested(TeamOut))
    pagination = Nested(PaginationSchema)


class TeamsView(MethodView):
    @app_team.input(TeamsQuery, location="query")
    @app_team.output(TeamsPage, status_code=200)
    @app_team.doc("List teams or search for them by name", responses=[200])
    def get(self, query_data):
        """
        Search teams. search_str + pagination.
        May return 0 results.
        """
        team_query = Team.query

        # TODO: better search?
        search_str = query_data.get("search_str")
        if search_str:
            team_query = team_query.filter(
                Team.display_name.ilike(f"%{search_str}%")  # type: ignore[reportAttributeAccessIssue]
            )

        pagination = team_query.paginate(
            page=query_data["page"], per_page=query_data["per_page"]
        )

        teams = pagination.items
        return {"teams": teams, "pagination": pagination_builder(pagination)}

    @app_team.auth_required(ryl_auth, roles=CRUD_AUTH_ROLES["team"].create)
    @app_team.input(TeamIn, location="json")
    @app_team.output(TeamOutMin, status_code=201)
    @app_team.doc("Add a team", responses=[409, 500])
    def post(self, json_data):
        """
        Add a team
        """
        current_app.logger.info(f"Request: Add team: {json_data}")
        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )

            new_team = try_add_team(
                ctx,
                name=json_data["name"],
                completeness_status=CompletenessStatus.user_edited,
                description=json_data.get("description", "No description."),
            )

            return new_team

        except RYLAlreadyExists as e:
            current_app.logger.warning(e)
            abort(409, e.message)

        except Exception as e:
            current_app.logger.warning(e)
            abort(500)


class TeamView(MethodView):
    @app_team.output(TeamOut, status_code=200)
    @app_team.doc("Get a team", responses=[404])
    def get(self, team_id):
        team = Team.query.filter_by(id=team_id).one_or_none()

        if not team:
            abort(404)

        return team

    @app_team.auth_required(ryl_auth, roles=CRUD_AUTH_ROLES["team"].update)
    @app_team.input(TeamPatch(partial=True))
    @app_team.output(TeamOutMin, status_code=200)
    @app_team.doc("Update a team", responses=[403, 404, 500])
    def patch(self, team_id, json_data):
        """
        Update a team with JSON data.
        """
        current_app.logger.info(f"Request: Patch team({team_id}): {json_data}")

        if team_id == 1:  # disallow updating default team
            abort(403, "You can't update this team")

        team_query = Team.query.filter_by(id=team_id)
        team: Team = team_query.one_or_none()
        if not team:
            abort(404)

        if not check_model_difference(team, json_data):
            raise RYLUpdateNoChange()

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )
            ctx.set()

            team_query.update(json_data)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)

        return team

    @app_team.auth_required(ryl_auth, roles=CRUD_AUTH_ROLES["team"].delete)
    @app_team.input(RYLContentIn(partial=True))
    @app_team.output({}, status_code=204)
    @app_team.doc("Delete a team (with note)", responses=[204, 401, 403, 404])
    def delete(self, team_id, json_data):
        current_app.logger.info(f"Request: Delete team: {team_id}")

        if team_id == 1:  # disallow deleting default team
            abort(403, "You can't delete this team")

        team = Team.query.filter_by(id=team_id).one_or_none()

        if not team:
            abort(404)

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )
            ctx.set()

            db.session.delete(team)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


app_team.add_url_rule("/v1/teams", view_func=TeamsView.as_view("teams"))
app_team.add_url_rule(
    "/v1/teams/<int:team_id>", view_func=TeamView.as_view("team")
)
