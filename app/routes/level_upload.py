from apiflask import (
    APIBlueprint,
    Schema,
    abort,
    pagination_builder,
)
from apiflask.fields import Integer, List, Nested, String
from apiflask.schemas import PaginationSchema
from apiflask.validators import Length
from apiflask.views import MethodView
from flask import current_app
from flask_jwt_extended import current_user

from app.db.database import CompletenessStatus, db
from app.db.models.gd_account import GDAccount
from app.db.models.level_upload import LevelUpload
from app.db.services.level_upload import get_level_upload, try_add_level_upload
from app.routes import PageSchema
from app.schemas import RYLContentIn
from app.schemas.level_upload import (
    LevelUploadIn,
    LevelUploadOut,
    LevelUploadOutMin,
    LevelUploadPatch,
)
from app.utility.auth import ryl_auth
from app.utility.context import ContextValues
from app.utility.crud_auth import CRUD_AUTH_ROLES
from app.utility.database import check_model_difference
from app.utility.error import RYLUpdateNoChange
from app.utility.exceptions import RYLAlreadyExists

app_level_upload = APIBlueprint("level_upload", __name__)


class LevelUploadsQuery(PageSchema):
    # search_str = GD Title
    search_str = String(required=False, validate=Length(1, 50))


class LevelUploadsPage(Schema):
    level_uploads = List(Nested(LevelUploadOutMin))
    pagination = Nested(PaginationSchema)


class LevelUploads(MethodView):
    @app_level_upload.input(LevelUploadsQuery, location="query")
    @app_level_upload.output(LevelUploadsPage, status_code=200)
    @app_level_upload.doc("List level uploads or search by GD title")
    def get(self, query_data):
        """
        Search level uploads. search_str + pagination.
        May return 0 results.
        """

        level_upload_query = LevelUpload.query

        # TODO: better search?
        search_str = query_data.get("search_str")
        if search_str:
            level_upload_query = level_upload_query.filter(
                LevelUpload.gd_title.ilike(f"%{search_str}%")  # type: ignore[reportAttributeAccessIssue]
            )

        pagination = level_upload_query.paginate(
            page=query_data["page"], per_page=query_data["per_page"]
        )

        uploads = pagination.items
        return {
            "level_uploads": uploads,
            "pagination": pagination_builder(pagination),
        }

    @app_level_upload.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["level_upload"].create
    )
    @app_level_upload.input(LevelUploadIn, location="json")
    @app_level_upload.output(LevelUploadOutMin, status_code=201)
    @app_level_upload.doc("Add a level upload manually", responses=[409, 500])
    def post(self, json_data):
        """
        Add a level upload manually.
        You probably don't want to use this.
        """
        current_app.logger.info(f"Request: Add level upload: {json_data}")

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )

            new_upload = try_add_level_upload(
                ctx=ctx,
                gdid=json_data["GD_ID"],
                gd_title=json_data["GD_title"],
                song_ng_id=json_data["song_NG_ID"],
                gd_account_id=json_data["GD_Account_id"],
                gd_rating=json_data["GD_rating"],
                gd_difficulty=json_data.get("gd_difficulty"),
                level_id=json_data.get("level_id"),
                gd_server_id=json_data["GD_server_id"],
                gd_cache_likes=None,
            )

            return new_upload, 201

        except RYLAlreadyExists as e:
            current_app.logger.warning(e)
            abort(409, e.message)
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


class LevelUploadView(MethodView):
    @app_level_upload.output(LevelUploadOut, status_code=200)
    @app_level_upload.doc("Get level upload by ID")
    def get(self, upload_id):
        level_upload = get_level_upload(upload_id)

        if not level_upload:
            abort(404)

        return level_upload

    @app_level_upload.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["level_upload"].update
    )
    @app_level_upload.input(LevelUploadPatch(partial=True), location="json")
    @app_level_upload.output(LevelUploadOutMin, status_code=200)
    @app_level_upload.doc("Update level upload", responses=[403, 404, 500])
    def patch(self, upload_id, json_data):
        """
        Update level upload with JSON data.
        """
        current_app.logger.info(
            f"Request: Patch level upload({upload_id}): {json_data}"
        )

        upload_query = LevelUpload.query.filter_by(id=upload_id)
        level_upload: LevelUpload = upload_query.one_or_none()
        if not level_upload:
            abort(404)

        if not check_model_difference(level_upload, json_data):
            raise RYLUpdateNoChange()

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )
            ctx.set()

            upload_query.update(json_data)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)

        return level_upload

    @app_level_upload.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["level_upload"].delete
    )
    @app_level_upload.input(RYLContentIn(partial=True), location="json")
    @app_level_upload.output({}, status_code=204)
    @app_level_upload.doc(
        "Delete level upload (with note)", responses=[204, 401, 403, 404]
    )
    def delete(self, upload_id, json_data):
        current_app.logger.info(f"Request: Delete level upload: {upload_id}")

        level_upload = get_level_upload(upload_id)

        if not level_upload:
            abort(404)

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note")
            )
            ctx.set()

            db.session.delete(level_upload)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


app_level_upload.add_url_rule(
    "/v1/level_uploads", view_func=LevelUploads.as_view("level_uploads")
)
app_level_upload.add_url_rule(
    "/v1/level_uploads/<int:upload_id>",
    view_func=LevelUploadView.as_view("level_upload"),
)
