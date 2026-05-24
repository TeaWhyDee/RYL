from apiflask import (
    APIBlueprint,
    PaginationSchema,
    Schema,
    abort,
    pagination_builder,
)
from apiflask.fields import Integer, List, Nested, String
from flask import current_app
from flask.views import MethodView
from flask_cors import cross_origin
from flask_jwt_extended import current_user

from app.db.database import db
from app.db.models.level import Level
from app.db.models.level_authorship import LevelAuthorship
from app.db.services.level_authorship import (
    get_level_authorship,
    try_add_level_authorship,
)
from app.routes import PageSchema
from app.schemas import RYLContentIn
from app.schemas.level_authorship import LevelAuthorshipIn, LevelAuthorshipOut
from app.utility.auth import ryl_auth
from app.utility.context import ContextValues
from app.utility.crud_auth import CRUD_AUTH_ROLES
from app.utility.error import RYLUpdateNoChange
from app.utility.exceptions import RYLAlreadyExists, RYLNotFound

app_level_authorship = APIBlueprint("level_authorship", __name__)


class LevelAuthorQuery(PageSchema):
    level_id = Integer(required=False)
    creator_id = Integer(required=False)
    team_id = Integer(required=False)


class LevelAuthorsPage(Schema):
    authors = List(Nested(LevelAuthorshipOut))
    pagination = Nested(PaginationSchema)


class LevelAuthorsView(MethodView):
    @app_level_authorship.input(LevelAuthorQuery, location="query")
    @app_level_authorship.output(LevelAuthorsPage, status_code=200)
    @app_level_authorship.doc(
        "List level authors or search for them", responses=[200]
    )
    def get(self, query_data):
        """
        List level author credits. Search/filter by various fields.
        May return 0 results.
        """
        query = LevelAuthorship.query

        level_id_filter = query_data.get("level_id")
        if level_id_filter:
            query = query.filter(LevelAuthorship.level_id == level_id_filter)

        creator_id_filter = query_data.get("creator_id")
        if creator_id_filter:
            query = query.filter(
                LevelAuthorship.creator_id == creator_id_filter
            )

        team_id_filter = query_data.get("team_id")
        if team_id_filter:
            query = query.filter(LevelAuthorship.team_id == team_id_filter)

        pagination = query.paginate(
            page=query_data["page"], per_page=query_data["per_page"]
        )
        authors = pagination.items

        return {
            "authors": authors,
            "pagination": pagination_builder(pagination),
        }

    @app_level_authorship.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["level_authorship"].create
    )
    @app_level_authorship.input(LevelAuthorshipIn, location="json")
    @app_level_authorship.output(LevelAuthorshipOut, status_code=201)
    @app_level_authorship.doc(
        "Add a level author credit", responses=[404, 409, 500]
    )
    def post(self, json_data):
        """
        Add a new level author credit (level to creator/team).
        Can only specify creator_id OR team_id, not both.
        """
        current_app.logger.info(f"Request: Add LevelAuthor: {json_data}")

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )

            new_author = try_add_level_authorship(
                ctx,
                level_id=json_data["level_id"],
                creator_id=json_data.get("creator_id"),
                team_id=json_data.get("team_id"),
            )

            return new_author

        except RYLNotFound as e:
            current_app.logger.warning(e)
            abort(404, e.message)

        except RYLAlreadyExists as e:
            current_app.logger.warning(e)
            abort(409, e.message)

        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


class LevelAuthorView(MethodView):
    @app_level_authorship.output(LevelAuthorshipOut, status_code=200)
    @app_level_authorship.doc("Get a level author credit", responses=[404])
    def get(self, authorship_id):
        """
        Get a specific Level Author credit by ID.
        """
        author = LevelAuthorship.query.filter_by(id=authorship_id).one_or_none()

        if not author:
            abort(404)

        return author

    # TODO
    # Patch: edit alias

    @app_level_authorship.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["level_authorship"].delete
    )
    @app_level_authorship.input(RYLContentIn(partial=True))
    @app_level_authorship.output({}, status_code=204)
    @app_level_authorship.doc(
        "Delete a level author credit (with note)",
        responses=[204, 401, 403, 404],
    )
    @cross_origin(allow_headers=["Content-Type", "Accept", "Authorization"])
    def delete(self, authorship_id, json_data):
        """
        Delete a Level Author credit (removes the link between level and creator/team).
        """
        current_app.logger.info(f"Request: Delete LevelAuthor: {authorship_id}")

        author = LevelAuthorship.query.filter_by(id=authorship_id).one_or_none()
        if not author:
            abort(404)

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )
            ctx.set()

            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)

        return "", 204


app_level_authorship.add_url_rule(
    "/v1/level_authorships",
    view_func=LevelAuthorsView.as_view("level_authorships"),
)
app_level_authorship.add_url_rule(
    "/v1/level_authorship/<int:authorship_id>",
    view_func=LevelAuthorView.as_view("level_authorship"),
)
