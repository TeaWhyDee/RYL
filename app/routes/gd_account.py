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
from flask_jwt_extended import current_user

from app import db
from app.db.models.gd_account import GDAccount
from app.db.services.gd_account import get_gd_account, try_add_gd_account
from app.routes import PageSchema
from app.schemas.gd_account import GDAccountIn, GDAccountOut, GDAccountPatch
from app.utility.auth import ryl_auth
from app.utility.context import ContextValues
from app.utility.crud_auth import CRUD_AUTH_ROLES
from app.utility.database import check_model_difference
from app.utility.error import RYLUpdateNoChange
from app.utility.exceptions import RYLAlreadyExists

app_gd_account = APIBlueprint("gd_account", __name__)


class GDAccountsQuery(PageSchema):
    search_str = String(required=False)
    server_id = Integer(required=False)


class GDAccountsPage(Schema):
    accounts = List(Nested(GDAccountOut))
    pagination = Nested(PaginationSchema)


class GDAccountsView(MethodView):
    @app_gd_account.input(GDAccountsQuery, location="query")
    @app_gd_account.output(GDAccountsPage, status_code=200)
    @app_gd_account.doc("List GD Accounts or search for them", responses=[200])
    def get(self, query_data):
        """
        List GD accounts. Optionally filter by search_str or server_id.
        """
        account_query = GDAccount.query

        search_str = query_data.get("search_str")
        if search_str:
            account_query = account_query.filter(
                GDAccount.username.ilike(f"%{search_str}%")
            )

        server_id = query_data.get("server_id")
        if server_id:
            account_query = account_query.filter(
                GDAccount.gd_server_id == server_id
            )

        pagination = account_query.paginate(
            page=query_data["page"], per_page=query_data["per_page"]
        )
        accounts = pagination.items

        return {
            "accounts": accounts,
            "pagination": pagination_builder(pagination),
        }

    @app_gd_account.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["gd_account"].create
    )
    @app_gd_account.input(GDAccountIn, location="json")
    @app_gd_account.output(GDAccountOut, status_code=201)
    @app_gd_account.doc("Add a GD account", responses=[409, 500])
    def post(self, json_data):
        """
        Add a new GD Account (for tracking level uploaders).
        """
        current_app.logger.info(f"Request: Add GDAccount: {json_data}")

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )

            new_account = try_add_gd_account(
                ctx,
                username=json_data["username"],
                gd_account_gdid=int(json_data["gd_account_gdid"]),
                gd_server_id=int(json_data["gd_server_id"]),
            )

            return new_account.to_dict()

        except RYLAlreadyExists as e:
            current_app.logger.warning(e)
            abort(409, e.message)

        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


class GDAccountView(MethodView):
    @app_gd_account.output(GDAccountOut, status_code=200)
    @app_gd_account.doc("Get a GD account", responses=[404])
    def get(self, account_id):
        """
        Get a specific GD Account by ID.
        """
        gd_account = GDAccount.query.filter_by(id=account_id).one_or_none()

        if not gd_account:
            abort(404)

        return gd_account

    @app_gd_account.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["gd_account"].update
    )
    @app_gd_account.input(GDAccountPatch(partial=True))
    @app_gd_account.output(GDAccountOut, status_code=200)
    @app_gd_account.doc("Update a GD account", responses=[403, 404, 500])
    def patch(self, account_id, json_data):
        """
        Update fields for a GD Account (username, gd_id, server).
        Requires moderator role to modify.
        """
        current_app.logger.info(
            f"Request: Patch GDAccount({account_id}): {json_data}"
        )

        query = GDAccount.query.filter_by(id=account_id)
        gd_account: GDAccount = query.one_or_none()

        if not check_model_difference(gd_account, json_data):
            raise RYLUpdateNoChange()

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )
            ctx.set()

            query.update(json_data)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)

        return gd_account

    @app_gd_account.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["gd_account"].delete
    )
    @app_gd_account.input(GDAccountIn(partial=True))
    @app_gd_account.output({}, status_code=204)
    @app_gd_account.doc(
        "Delete a GD account (with note)", responses=[204, 401, 403, 404]
    )
    def delete(self, account_id, json_data):
        """
        Delete a GD Account.
        """
        current_app.logger.info(f"Request: Delete GDAccount: {account_id}")

        gd_account = GDAccount.query.filter_by(id=account_id).one_or_none()

        if not gd_account:
            abort(404)

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )
            ctx.set()

            db.session.delete(gd_account)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


app_gd_account.add_url_rule(
    "/v1/gd_accounts", view_func=GDAccountsView.as_view("gd_accounts")
)
app_gd_account.add_url_rule(
    "/v1/gd_accounts/<int:account_id>",
    view_func=GDAccountView.as_view("gd_account"),
)
