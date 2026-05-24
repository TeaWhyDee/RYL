from apiflask import APIBlueprint, Schema, abort, pagination_builder
from apiflask.fields import Enum, Integer, List, Nested
from apiflask.views import MethodView
from flask import current_app
from flask_jwt_extended import current_user

from app.db.database import db
from app.db.models.credit import LevelCredit
from app.db.models.user import UserRole
from app.db.services.credit import try_add_credit
from app.routes import PageSchema
from app.schemas import RYLContentIn
from app.schemas.credit import (
    LevelCreditIn,
    LevelCreditOut,
    LevelCreditPatch,
)
from app.utility.auth import ryl_auth
from app.utility.context import ContextValues
from app.utility.crud_auth import CRUD_AUTH_ROLES
from app.utility.database import check_model_difference
from app.utility.error import RYLUpdateNoChange
from app.utility.exceptions import RYLAlreadyExists

app_credit = APIBlueprint("level_credit", __name__)


class LevelCreditQuery(PageSchema):
    level_id = Integer(required=False)
    creator_id = Integer(required=False)


class CreditsPage(Schema):
    credits = List(Nested(LevelCreditOut))
    pagination = PageSchema


class CreditsView(MethodView):
    @app_credit.input(LevelCreditQuery, location="query")
    @app_credit.output(CreditsPage, status_code=200)
    @app_credit.doc(
        "List credits or search by level_id and/or creator_id", responses=[200]
    )
    def get(self, query_data):
        query = LevelCredit.query

        if query_data.get("level_id"):
            query = query.filter_by(level_id=query_data["level_id"])

        if query_data.get("creator_id"):
            query = query.filter_by(creator_id=query_data["creator_id"])

        pagination = query.paginate(
            page=query_data["page"], per_page=query_data["per_page"]
        )
        level_credits = pagination.items

        return {
            "credits": level_credits,
            "pagination": pagination_builder(pagination),
        }

    @app_credit.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["level_credit"].create
    )
    @app_credit.input(LevelCreditIn, location="json")
    @app_credit.output(LevelCreditOut, status_code=201)
    @app_credit.doc("Add a credit", responses=[409, 500])
    def post(self, json_data):
        """
        Add a credit to a level.
        """
        current_app.logger.info(f"Request: Add credit: {json_data}")

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )

            new_credit = try_add_credit(
                ctx=ctx,
                level_id=json_data["level_id"],
                creator_id=json_data["creator_id"],
                creator_role=json_data["creator_role"],
            )

            return new_credit

        except RYLAlreadyExists as e:
            current_app.logger.warning(e)
            abort(409, e.message)

        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


class CreditView(MethodView):
    @app_credit.output(LevelCreditOut, status_code=200)
    @app_credit.doc("Get a levelcredit", responses=[404])
    def get(self, credit_id):
        credit = LevelCredit.query.filter_by(id=credit_id).one_or_none()
        if not credit:
            abort(404)

        return credit

    @app_credit.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["level_credit"].update
    )
    @app_credit.input(LevelCreditPatch(partial=True))
    @app_credit.output(LevelCreditOut, status_code=200)
    @app_credit.doc("Update a level credit", responses=[403, 404, 500])
    def patch(self, credit_id, json_data):
        """
        Update a credit with JSON data.
        """
        current_app.logger.info(
            f"Request: Patch credit({credit_id}): {json_data}"
        )

        credit_query = LevelCredit.query.filter_by(id=credit_id)
        credit = credit_query.one_or_none()
        if not credit:
            abort(404)

        if not check_model_difference(credit, json_data):
            raise RYLUpdateNoChange()

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )
            ctx.set()

            credit_query.update(json_data)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)

        return credit

    @app_credit.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["level_credit"].delete
    )
    @app_credit.input(RYLContentIn(partial=True))
    @app_credit.output({}, status_code=204)
    @app_credit.doc(
        "Delete a credit (with note)", responses=[204, 401, 403, 404]
    )
    def delete(self, credit_id, json_data):
        current_app.logger.info(f"Request: Delete credit: {credit_id}")

        credit = LevelCredit.query.filter_by(id=credit_id).one_or_none()

        if not credit:
            abort(404)

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note")
            )
            ctx.set()

            db.session.delete(credit)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


app_credit.add_url_rule(
    "/v1/level_credits",
    view_func=CreditsView.as_view("level_credits"),
)

app_credit.add_url_rule(
    "/v1/level_credits/<int:credit_id>",
    view_func=CreditView.as_view("level_credit"),
)
