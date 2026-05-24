from apiflask import APIBlueprint, Schema, abort, pagination_builder
from apiflask.fields import Integer, List, Nested, String
from apiflask.views import MethodView
from flask_httpauth import current_app
from flask_jwt_extended import current_user

from app.db.database import db
from app.db.models.level_genre import LevelGenre
from app.db.services.level_genre import (
    get_level_genre,
    get_level_genres,
    try_add_level_genre,
)
from app.routes import PageSchema
from app.schemas import RYLContentIn
from app.schemas.level_genre import LevelGenreIn, LevelGenreOutMin
from app.utility.auth import ryl_auth
from app.utility.context import ContextValues
from app.utility.crud_auth import CRUD_AUTH_ROLES
from app.utility.exceptions import RYLAlreadyExists

app_level_genre = APIBlueprint("level_genre", __name__)


class LevelGenresQuery(PageSchema):
    level_id = Integer(required=False)
    genre_id = Integer(required=False)


class LevelGenresPage(Schema):
    level_genres = List(Nested(LevelGenreOutMin))
    pagination = Nested(PageSchema)


class LevelGenres(MethodView):
    @app_level_genre.input(LevelGenresQuery, location="query")
    @app_level_genre.output(LevelGenresPage)
    @app_level_genre.doc(
        "Search for level-genre associations by level_id and/or genre_id"
    )
    def get(self, query_data):
        """Get all genres associated with a level."""
        level_id = query_data.get("level_id")
        genre_id = query_data.get("genre_id")

        level_genre_query = LevelGenre.query
        if level_id:
            level_genre_query = level_genre_query.filter_by(level_id=level_id)

        if genre_id:
            level_genre_query = level_genre_query.filter_by(genre_id=genre_id)

        pagination = level_genre_query.paginate(
            page=query_data["page"], per_page=query_data["per_page"]
        )

        level_genres = pagination.items
        return {
            "level_genres": level_genres,
            "pagination": pagination_builder(pagination),
        }

    @app_level_genre.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["level_genre"].create
    )
    @app_level_genre.input(LevelGenreIn, location="json")
    @app_level_genre.output(LevelGenreOutMin, status_code=201)
    @app_level_genre.doc(
        "Add a genre association for a level", responses=[409, 500]
    )
    def post(self, json_data):
        """Add a specific genre to a level."""
        current_app.logger.info(f"Request: Add level_genre: {json_data}")

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )

            new_assoc = try_add_level_genre(
                ctx=ctx,
                level_id=json_data["level_i_id"],
                genre_id=json_data["genre_id"],
            )

            return new_assoc, 201

        except RYLAlreadyExists as e:
            current_app.logger.error(e)
            abort(409, e.message)

        except Exception as e:
            current_app.logger.error(e)
            abort(500)


class LevelGenreView(MethodView):
    @app_level_genre.output(LevelGenreOutMin)
    @app_level_genre.doc("Get specific association by ID")
    def get(self, lg_id):
        level_genre = get_level_genre(lg_id)

        if not level_genre:
            abort(404)

        return level_genre

    @app_level_genre.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["level_genre"].delete
    )
    @app_level_genre.input(RYLContentIn, location="json")
    @app_level_genre.output({}, status_code=204)
    @app_level_genre.doc(
        "Remove genre association from level", responses=[204, 401, 403, 404]
    )
    def delete(self, level_genre_id, json_data):
        """Delete specific association."""
        level_genre = get_level_genre(level_genre_id)

        if not level_genre:
            abort(404)

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )
            ctx.set()

            db.session.delete(level_genre)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


app_level_genre.add_url_rule(
    "/v1/level_genres",
    view_func=LevelGenres.as_view("level_genres"),
)
app_level_genre.add_url_rule(
    "/v1/level_genres/<int:assoc_id>",
    view_func=LevelGenreView.as_view("level_genre"),
)
