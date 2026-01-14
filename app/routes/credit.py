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

from app.db.database import db
from app.db.models.credit import LevelCredit
from app.db.services.credit import add_or_get_credit
from app.schemas.credit import (
    CreditIn,
    CreditOut,
)

# from app.schemas.level import LevelIn, LevelOut, LevelOutExtra
from app.utility.auth import auth
from app.utility.context import ContextValues

app_credit = APIBlueprint("credit", __name__)


class CreditQuery(Schema):
    page = Integer(load_default=1)
    level_id = Integer()
    creator_id = Integer()
    per_page = Integer(load_default=20, validate=Range(min=1, max=100))


class CreditsPage(Schema):
    credits = List(Nested(CreditOut))
    pagination = Nested(PaginationSchema)


class Credits(MethodView):
    # @app_level.output(LevelOut(many=True))
    @app_credit.input(CreditQuery, location="query")
    @app_credit.output(CreditsPage)
    @app_credit.doc("Get level credits (paginated)")
    def get(self, query_data):
        query = LevelCredit.query

        if "level_id" in query_data:
            level_id = query_data["level_id"]
            query = query.filter_by(level_id=level_id)

        if "creator_id" in query_data:
            creator_id = query_data["creator_id"]
            query = query.filter_by(creator_id=creator_id)

        pagination = query.paginate(
            page=query_data["page"], per_page=query_data["per_page"]
        )

        credits = pagination.items
        return {
            "credits": credits,
            "pagination": pagination_builder(pagination),
        }

    @app_credit.input(CreditIn, location="json")
    @app_credit.output(CreditOut, status_code=201)
    @app_credit.auth_required(auth)
    @app_credit.doc("Add a credit")
    def post(self, json_data):
        try:
            new_credit = add_or_get_credit(
                ContextValues(),
                json_data["level_id"],
                json_data["creator_id"],
                json_data["creator_role"],
            )
        except Exception as e:
            current_app.logger.warning(e)
            abort(500)

        return new_credit


class CreditView(MethodView):
    decorators = [
        app_credit.doc(responses=[404]),
    ]

    @app_credit.output(CreditOut)
    def get(self, credit_id):
        credit = LevelCredit.query.filter_by(id=credit_id).one_or_none()

        return credit

    @app_credit.output({}, status_code=204)
    def delete(self, credit_id):
        credit = LevelCredit.query.filter_by(id=credit_id).one_or_none()

        if not credit:
            abort(404)

        db.session.delete(credit)
        db.session.commit()

    # @app_level.input(LevelIn)
    # @app_level.output(LevelOut)
    # def put(self, level_id, json_data):
    #     pass

    # @app_level.input(LevelIn(partial=True))
    # @app_level.output(LevelOut)
    # def patch(self, level_id, json_data):
    #     pass


# @app_credit.output(LevelCreditsPage)
# @app_credit.auth_required(auth)
# @app_credit.doc("Get level credits (paginated)")
# @app_credit.get("/level/")
# def get(self, query_data):
#     level_id = query_data["level_id"]
#
#     pagination = LevelCredit.query.filter_by(level_id=level_id).paginate(
#         page=query_data["page"], per_page=query_data["per_page"]
#     )
#
#     credits = pagination.items
#     return Credits


app_credit.add_url_rule(
    "/v1/level_credits", view_func=Credits.as_view("level_credits")
)
app_credit.add_url_rule(
    "/v1/level_credits/<int:credit_id>",
    view_func=CreditView.as_view("level_credit"),
)
