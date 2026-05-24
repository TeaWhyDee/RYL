from apiflask import APIBlueprint, Schema, abort, pagination_builder
from apiflask.fields import List, Nested, String
from apiflask.views import MethodView
from flask import current_app
from flask_jwt_extended import current_user

from app.db.database import db
from app.db.models.genre import Genre
from app.db.services.genre import get_genre, try_add_genre
from app.routes import PageSchema
from app.schemas import RYLContentIn
from app.schemas.genre import GenreIn, GenreOut, GenrePatch
from app.utility.auth import ryl_auth
from app.utility.context import ContextValues
from app.utility.crud_auth import CRUD_AUTH_ROLES
from app.utility.database import check_model_difference
from app.utility.error import RYLUpdateNoChange
from app.utility.exceptions import RYLAlreadyExists

app_genre = APIBlueprint("genre", __name__)


class GenresQuery(PageSchema):
    search_str = String(required=False)


class GenresPage(Schema):
    genres = List(Nested(GenreOut))
    pagination = Nested(PageSchema)


class Genres(MethodView):
    @app_genre.input(GenresQuery, location="query")
    @app_genre.output(GenresPage)
    @app_genre.doc("List Genres. Search by genre name.")
    def get(self, query_data):
        """List genres with optional search by name."""

        query = Genre.query.order_by(Genre.created_at.desc())

        search_str = query_data.get("search_str")
        if search_str:
            query = query.filter(Genre.display_name.ilike(f"%{search_str}%"))

        pagination = query.paginate(
            page=query_data["page"], per_page=query_data["per_page"]
        )

        return {
            "genres": pagination.items,
            "pagination": pagination_builder(pagination),
        }

    @app_genre.auth_required(ryl_auth, roles=CRUD_AUTH_ROLES["genre"].create)
    @app_genre.input(GenreIn, location="json")
    @app_genre.output(GenreOut, status_code=201)
    @app_genre.doc("Add a new genre", responses=[409])
    def post(self, json_data):
        """Manually add a new genre."""
        current_app.logger.info(f"Request: Add genre: {json_data}")

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )

            new_genre = try_add_genre(
                ctx=ctx,
                name=json_data["name"],
                description=json_data.get("description"),
            )
            return new_genre, 201

        except RYLAlreadyExists as e:
            current_app.logger.warning(e)
            abort(409, e.message)

        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


class GenreView(MethodView):
    @app_genre.output(GenreOut)
    @app_genre.doc("Get genre by ID")
    def get(self, genre_id):
        """Get a specific genre."""
        genre = get_genre(genre_id)

        if not genre:
            abort(404)

        return genre

    @app_genre.auth_required(ryl_auth, roles=CRUD_AUTH_ROLES["genre"].update)
    @app_genre.input(GenrePatch(partial=True), location="json")
    @app_genre.output(GenreOut)
    @app_genre.doc("Update genre details")
    def patch(self, genre_id, json_data):
        """Update genre display name or description."""

        genre_query = Genre.query.filter_by(id=genre_id)
        genre: Genre = genre_query.one_or_none()
        if not genre:
            abort(404)

        if not check_model_difference(genre, json_data):
            raise RYLUpdateNoChange()

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )
            ctx.set()

            genre_query.update(json_data)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)

        return genre

    @app_genre.auth_required(ryl_auth, roles=CRUD_AUTH_ROLES["genre"].delete)
    @app_genre.input(RYLContentIn(partial=True), location="json")
    @app_genre.output({}, status_code=204)
    @app_genre.doc("Delete a genre", responses=[404])
    def delete(self, genre_id, json_data):
        """Delete a genre."""
        current_app.logger.info(f"Request: Delete genre: {genre_id}")

        genre = get_genre(genre_id)

        if not genre:
            abort(404)

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note")
            )
            ctx.set()

            db.session.delete(genre)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


app_genre.add_url_rule("/v1/genres", view_func=Genres.as_view("genres"))
app_genre.add_url_rule(
    "/v1/genres/<int:genre_id>", view_func=GenreView.as_view("genre")
)
