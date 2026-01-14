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
from sqlalchemy import select

from app.db.database import db
from app.db.models.level import Level, LevelType
from app.schemas.level import LevelIn, LevelOut, LevelOutExtra, LevelPatch
from app.utility.auth import auth

app_level = APIBlueprint("level", __name__)


class LevelQuery(Schema):
    page = Integer(load_default=1)
    level_type = Enum(LevelType)
    creator_id = Integer()
    # set default value to 20, and make sure the value is less than 30
    per_page = Integer(load_default=20, validate=Range(min=1, max=100))


class LevelsPage(Schema):
    levels = List(Nested(LevelOutExtra))
    pagination = Nested(PaginationSchema)


class Levels(MethodView):
    # @app_level.output(LevelOut(many=True))
    @app_level.input(LevelQuery, location="query")
    @app_level.output(LevelsPage)
    @app_level.doc("Search levels (paginated)")
    @app_level.auth_required(auth, optional="True")
    # @app_level.auth_required(auth)
    def get(self, query_data):
        # query = Level.query
        query = select(Level)
        if "level_type" in query_data:
            level_type = query_data["level_type"]
            query = query.where(Level.level_type == level_type)

        if "creator_id" in query_data:
            creator_id = query_data["creator_id"]
            query = query.filter_by(creator_id=creator_id)

        query = query.order_by(Level.id.desc())
        pagination = db.paginate(query)

        levels = pagination.items
        return {"levels": levels, "pagination": pagination_builder(pagination)}

    @app_level.input(LevelIn, location="json")
    @app_level.output(LevelOut, status_code=201)
    @app_level.doc("Add a level")
    @app_level.auth_required(auth)
    def post(self, json_data):
        try:
            current_app.logger.warning(json_data)

            new_level = Level(
                GD_id=json_data["GD_id"],
                name=json_data["name"],
                GD_publisher=json_data["GD_publisher"],
                # creator_id=json_data["creator_id"],
                level_type=json_data["level_type"],
                level_length=json_data["length"],
                level_rating=json_data["rating"],
            )

            db.session.add(new_level)
            db.session.commit()
        except Exception as e:
            current_app.logger.warning(e)
            abort(500)

        return new_level


class LevelView(MethodView):
    decorators = [app_level.doc(responses=[404])]

    @app_level.output(LevelOut)
    def get(self, level_id):
        level = Level.query.filter_by(id=level_id).one_or_none()

        return level

    @app_level.output({}, status_code=204)
    @app_level.auth_required(auth)
    def delete(self, level_id):
        level = Level.query.filter_by(id=level_id).one_or_none()

        if not level:
            abort(404)

        db.session.delete(level)
        db.session.commit()

    # @app_level.input(LevelIn)
    # @app_level.output(LevelOut)
    # @app_level.auth_required(auth)
    # def put(self, level_id, json_data):
    #     pass

    @app_level.input(LevelPatch(partial=True))
    @app_level.output(LevelOut)
    @app_level.auth_required(auth)
    def patch(self, level_id, json_data):
        level_query = Level.query.filter_by(id=level_id)

        level = level_query.one_or_none()
        if not level:
            abort(404)

        try:
            level_query.update(json_data)
            db.session.commit()
        except Exception as e:
            abort(500, f"{e}")

        return level


@app_level.get("/v1/level_by_url/<string:url_name>")
@app_level.output(LevelOut)
def get_by_url_name(url_name):
    level = Level.query.filter_by(url_name=url_name).one_or_none()

    if not level:
        abort(404)

    return level


app_level.add_url_rule("/v1/levels", view_func=Levels.as_view("levels"))
app_level.add_url_rule(
    "/v1/levels/<int:level_id>", view_func=LevelView.as_view("level")
)
