import json

from apiflask import (
    APIBlueprint,
    PaginationSchema,
    Schema,
    abort,
    pagination_builder,
)
from apiflask.fields import Enum, Integer, List, Nested, String
from apiflask.validators import Range
from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import current_user
from sqlalchemy import Table, or_
from sqlalchemy.exc import NoResultFound

from app.db.database import CompletenessStatus, audit_md, db
from app.db.models.creator import Creator
from app.db.models.level import GDVersion, Level, LevelType
from app.db.models.level_authorship import LevelAuthorship
from app.db.models.level_genre import LevelGenre
from app.db.models.level_upload import LevelUpload
from app.db.services.level import get_level, get_level_by_url_name
from app.routes import PageSchema
from app.schemas import RYLContentIn
from app.schemas.level import LevelIn, LevelOut, LevelOutExtra, LevelPatch
from app.schemas.level_genre import LevelGenreOutExtra
from app.utility.auth import ryl_auth
from app.utility.context import ContextValues
from app.utility.crud_auth import CRUD_AUTH_ROLES
from app.utility.database import check_model_difference
from app.utility.error import RYLUpdateNoChange
from app.utility.util import sanitize_for_url

app_level = APIBlueprint("level", __name__)


class LevelQuery(PageSchema):
    level_type = Enum(LevelType)
    creator_id = Integer()
    search_str = String()
    version = Enum(GDVersion)
    # TODO: more search options


class LevelsPage(Schema):
    levels = List(Nested(LevelOutExtra))
    pagination = Nested(PaginationSchema)


class Levels(MethodView):
    @app_level.input(LevelQuery, location="query")
    @app_level.output(LevelsPage)
    @app_level.doc("Search levels (paginated)")
    def get(self, query_data):
        """
        Search levels. search_str + pagination.
        May return 0 results.
        """
        level_query = Level.query

        # Search Params
        level_type = query_data.get("level_type")
        if level_type:
            level_query = level_query.filter_by(level_type=level_type)

        # creator_id = query_data.get("creator_id")
        # if creator_id:
        #     level_query = level_query.filter_by(creator_id=creator_id)

        search_str = query_data.get("search_str")
        if search_str:
            level_query = (
                level_query.join(Level.authorships)
                .join(Creator, Creator.id == LevelAuthorship.creator_id)
                .filter(
                    or_(
                        Creator.display_name.ilike(f"%{search_str}%"),  # type: ignore[reportAttributeAccessIssue]
                        Level.display_name.ilike(f"%{search_str}%"),  # type: ignore[reportAttributeAccessIssue]
                    )
                )
            )

        filter_version = query_data.get("version")
        if filter_version:
            level_query = level_query.filter(Level.GD_version == filter_version)

        # Paginate
        level_query = level_query.order_by(Level.id.desc())

        pagination = level_query.paginate(
            page=query_data["page"], per_page=query_data["per_page"]
        )

        levels = pagination.items
        return {"levels": levels, "pagination": pagination_builder(pagination)}

    @app_level.auth_required(ryl_auth, roles=CRUD_AUTH_ROLES["level"].create)
    @app_level.input(LevelIn, location="json")
    @app_level.output(LevelOut, status_code=201)
    @app_level.doc("Add a level")
    def post(self, json_data):
        try:
            current_app.logger.warning(json_data)
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )

            url_name = sanitize_for_url(json_data["name"])
            new_level = Level(
                GD_id=json_data["GD_id"],
                display_name=json_data["name"],
                url_name=url_name,
                completeness_status=CompletenessStatus.user_edited,
                # GD_publisher=json_data["GD_publisher"],
                # creator_id=json_data["creator_id"],
                level_type=json_data["level_type"],
                level_length=json_data["length"],
                level_rating=json_data["rating"],
            )

            ctx.set()
            db.session.add(new_level)
            db.session.commit()
        except Exception as e:
            current_app.logger.warning(e)
            abort(500)

        return new_level


class LevelView(MethodView):
    decorators = [app_level.doc(responses=[404])]

    @app_level.output(LevelOutExtra)
    @app_level.doc("Get a level", responses=[404])
    def get(self, level_url_name: str):
        level = get_level_by_url_name(level_url_name)

        if not level:
            abort(404)

        return level

    @app_level.auth_required(ryl_auth, roles=CRUD_AUTH_ROLES["level"].update)
    @app_level.input(LevelPatch(partial=True))
    @app_level.output(LevelOut)
    @app_level.doc("Update a level", responses=[403, 404, 500])
    def patch(self, level_id, json_data):
        """
        Update a level with JSON data.
        """
        current_app.logger.info(
            f"Request: Patch level({level_id}): {json_data}"
        )

        level_query = Level.query.filter_by(id=level_id)
        level = level_query.one_or_none()
        if not level:
            abort(404)

        if not check_model_difference(level, json_data):
            raise RYLUpdateNoChange()

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )
            ctx.set()

            level_query.update(json_data)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)

        return level

    @app_level.auth_required(ryl_auth, roles=CRUD_AUTH_ROLES["level"].delete)
    @app_level.input(RYLContentIn(partial=True))
    @app_level.output({}, status_code=204)
    @app_level.doc("Delete a level (with note)", responses=[204, 401, 403, 404])
    def delete(self, level_id, json_data):
        current_app.logger.info(f"Request: Delete level: {level_id}")

        level = Level.query.filter_by(id=level_id).one_or_none()

        if not level:
            abort(404)

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note")
            )
            ctx.set()

            db.session.delete(level)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


# @app_level.get("/v1/level_by_url/<string:url_name>")
# @app_level.output(LevelOut)
# def get_by_url_name(url_name):
#     level = Level.query.filter_by(url_name=url_name).one_or_none()
#
#     if not level:
#         abort(404)
#
#     return level


def get_audit_json(audit_table_name, filter_params):
    audit_table = Table(audit_table_name, audit_md, autoload_with=db.engine)
    stmt = audit_table.select().filter_by(**filter_params)

    audit_rows = db.engine.connect().execute(stmt)
    res = [dict(x) for x in audit_rows.mappings()]

    return res


@app_level.get("/v1/level/<int:level_id>/audit")
@app_level.doc("Get history of changes")
def get_audit(level_id):
    """Get history of changes related to the level"""

    res_level = get_audit_json("levels_audit", {"id": level_id})
    res_authors = get_audit_json("level_authors_audit", {"level_id": level_id})

    res = {"level": res_level, "authorships": res_authors}

    return json.dumps(res, default=str)


@app_level.get("/v1/level/<int:level_id>/genres")
@app_level.output(LevelGenreOutExtra(many=True))
@app_level.doc("List genres for a specific level")
def get_genres(level_id):
    """Get all genres associated with a level."""

    level_genre_query = LevelGenre.query.filter_by(level_id=level_id)
    level_genres = level_genre_query.all()

    return level_genres


app_level.add_url_rule("/v1/levels", view_func=Levels.as_view("levels"))
# app_level.add_url_rule(
#     "/v1/levels/<int:level_id>", view_func=LevelView.as_view("level")
# )
app_level.add_url_rule(
    "/v1/levels/<string:level_url_name>", view_func=LevelView.as_view("level")
)
