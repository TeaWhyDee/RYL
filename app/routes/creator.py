from apiflask import (
    APIBlueprint,
    PaginationSchema,
    Schema,
    abort,
    pagination_builder,
)
from apiflask.fields import Integer, List, Nested, String
from apiflask.validators import Range
from flask import current_app, json
from flask.views import MethodView
from flask_jwt_extended import current_user
from sqlalchemy_declarative_extensions.audit import set_context_values

from app.db.database import db
from app.db.models.creator import Creator
from app.schemas.creator import CreatorIn, CreatorOut
from app.utility.auth import auth

app_creator = APIBlueprint("creator", __name__)


class CreatorQuery(Schema):
    page = Integer(load_default=1)
    # set default value to 20, and make sure the value is less than 30
    per_page = Integer(load_default=20, validate=Range(min=1, max=100))


class CreatorsPage(Schema):
    creators = List(Nested(CreatorOut))
    pagination = Nested(PaginationSchema)


class Creators(MethodView):
    @app_creator.input(CreatorQuery, location="query")
    @app_creator.output(CreatorsPage)
    @app_creator.doc("Search for creators (paginated)")
    def get(self, query_data):
        pagination = Creator.query.order_by(Creator.id.desc()).paginate(
            page=query_data["page"], per_page=query_data["per_page"]
        )

        creators = pagination.items

        return {
            "creators": creators,
            "pagination": pagination_builder(pagination),
        }

    @app_creator.input(CreatorIn, location="json")
    @app_creator.output(CreatorOut, status_code=201)
    @app_creator.doc("Add a creator")
    @app_creator.auth_required(auth)
    def post(self, json_data):
        try:
            new_creator = Creator(name=json_data["name"])

            db.session.add(new_creator)
            db.session.commit()
        except Exception as e:
            current_app.logger.warning(e)
            abort(500)

        return new_creator


class CreatorView(MethodView):
    decorators = [app_creator.doc(responses=[404])]

    @app_creator.output(CreatorOut)
    @app_creator.doc("Get Creator by ID")
    def get(self, creator_id):
        creator = Creator.query.filter_by(id=creator_id).one_or_none()

        if not creator:
            abort(404)

        return creator

    @app_creator.output({}, status_code=204)
    @app_creator.doc("Delete creator by ID")
    def delete(self, creator_id):
        creator = Creator.query.filter_by(id=creator_id).one_or_none()

        if not creator:
            abort(404)

        db.session.delete(creator)
        db.session.commit()

    # @app_creator.input(CreatorIn)
    # @app_creator.output(CreatorOut)
    # @app_creator.doc("Not implemented")
    # def put(self, creator_id, json_data):
    #     pass

    # @app_creator.input(CreatorIn(partial=True))
    # @app_creator.output(CreatorOut)
    # @app_creator.doc("Not implemented")
    # def patch(self, creator_id, json_data):
    #     pass


@app_creator.get("/v1/creator_by_url/<string:url_name>")
@app_creator.output(CreatorOut)
def get_by_url_name(url_name):
    creator = Creator.query.filter_by(url_name=url_name).one_or_none()

    if not creator:
        abort(404)

    return creator


app_creator.add_url_rule("/v1/creators", view_func=Creators.as_view("creators"))
app_creator.add_url_rule(
    "/v1/creator/<int:creator_id>", view_func=CreatorView.as_view("creator")
)
