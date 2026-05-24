from apiflask import (
    APIBlueprint,
    PaginationSchema,
    Schema,
    abort,
    pagination_builder,
)
from apiflask.fields import Integer, List, Nested, String
from apiflask.validators import Length, Range
from flask import current_app, json
from flask.views import MethodView
from flask_jwt_extended import current_user
from sqlalchemy_declarative_extensions.audit import set_context_values

from app.db.database import CompletenessStatus, db
from app.db.models.creator import Creator
from app.db.services.creator import try_add_creator
from app.routes import PageSchema
from app.schemas import RYLContentIn
from app.schemas.creator import CreatorIn, CreatorOut, CreatorPatch
from app.utility.auth import ryl_auth
from app.utility.context import ContextValues
from app.utility.crud_auth import CRUD_AUTH_ROLES
from app.utility.database import check_model_difference
from app.utility.error import RYLUpdateNoChange
from app.utility.exceptions import RYLAlreadyExists

app_creator = APIBlueprint("creator", __name__)


class CreatorQuery(PageSchema):
    search_str = String(required=False, validate=Length(1, 50))


class CreatorsPage(Schema):
    creators = List(Nested(CreatorOut))
    pagination = Nested(PaginationSchema)


class Creators(MethodView):
    @app_creator.input(CreatorQuery, location="query")
    @app_creator.output(CreatorsPage)
    @app_creator.doc("Search for creators (paginated)")
    def get(self, query_data):
        """
        Search creators. search_str + pagination.
        May return 0 results.
        """
        creator_query = Creator.query

        # TODO: better search?
        search_str = query_data.get("search_str")
        if search_str:
            creator_query = creator_query.filter(
                Creator.display_name.ilike(f"%{search_str}%")  # type: ignore[reportAttributeAccessIssue]
            )

        pagination = creator_query.paginate(
            page=query_data["page"], per_page=query_data["per_page"]
        )

        creators = pagination.items

        return {
            "creators": creators,
            "pagination": pagination_builder(pagination),
        }

    @app_creator.input(CreatorIn, location="json")
    @app_creator.output(CreatorOut, status_code=201)
    @app_creator.doc("Add a creator", responses=[409, 500])
    @app_creator.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["creator"].create
    )
    def post(self, json_data):
        """
        Add a creator
        """
        current_app.logger.info(f"Request: Add creator: {json_data}")

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )
            new_creator = try_add_creator(
                ctx=ctx,
                name=json_data["display_name"],
                completeness_status=CompletenessStatus.imported_GD,
                description=json_data.get("description", "No description."),
            )

            return new_creator

        except RYLAlreadyExists as e:
            current_app.logger.warning(e)
            abort(409, e.message)

        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


class CreatorView(MethodView):
    decorators = [app_creator.doc(responses=[404])]

    @app_creator.output(CreatorOut, status_code=200)
    @app_creator.doc("Get Creator by ID")
    def get(self, creator_id):
        creator = Creator.query.filter_by(id=creator_id).one_or_none()

        if not creator:
            abort(404)

        return creator

    @app_creator.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["creator"].update
    )
    @app_creator.input(CreatorPatch(partial=True), location="json")
    @app_creator.output(CreatorOut, status_code=200)
    @app_creator.doc("Update a creator", responses=[403, 404, 500])
    def patch(self, creator_id, json_data):
        """
        Update a creator with JSON data.
        """
        current_app.logger.info(
            f"Request: Patch creator({creator_id}): {json_data}"
        )

        creator_query = Creator.query.filter_by(id=creator_id)
        creator: Creator = creator_query.one_or_none()
        if not creator:
            abort(404)

        if creator_id == 1:
            abort(403, "You can't update this creator")

        if not check_model_difference(creator, json_data):
            raise RYLUpdateNoChange()

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )
            ctx.set()

            creator_query.update(json_data)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)

        return creator

    @app_creator.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["creator"].delete
    )
    @app_creator.input(RYLContentIn(partial=True), location="json")
    @app_creator.output({}, status_code=204)
    @app_creator.doc(
        "Delete creator (with note)", responses=[204, 401, 403, 404]
    )
    def delete(self, creator_id, json_data):
        current_app.logger.info(f"Request: Delete creator: {creator_id}")
        creator = Creator.query.filter_by(id=creator_id).one_or_none()

        if not creator:
            abort(404)

        if creator_id == 1:  # disallow deleting default creator
            abort(403, "You can't delete this creator")

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note")
            )
            ctx.set()

            db.session.delete(creator)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


# @app_creator.get("/v1/creator_by_url/<string:url_name>")
# @app_creator.output(CreatorOut)
# def get_by_url_name(url_name):
#     creator = Creator.query.filter_by(url_name=url_name).one_or_none()
#
#     if not creator:
#         abort(404)
#
#     return creator


app_creator.add_url_rule("/v1/creators", view_func=Creators.as_view("creators"))
app_creator.add_url_rule(
    "/v1/creator/<int:creator_id>", view_func=CreatorView.as_view("creator")
)
