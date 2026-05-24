from apiflask import APIBlueprint, PaginationSchema, Schema, abort
from apiflask.fields import Enum, Integer, List, Nested, String
from apiflask.validators import Length
from apiflask.views import MethodView
from flask import current_app
from flask_jwt_extended import current_user

from app.db.database import CompletenessStatus, db
from app.db.models.gd_server import GDServer
from app.db.models.level import GDVersion
from app.db.services.gd_server import get_gd_server, try_add_gd_server
from app.routes import PageSchema
from app.schemas import RYLContentIn
from app.schemas.gd_server import GDServerIn, GDServerOut, GDServerPatch
from app.utility.auth import ryl_auth
from app.utility.context import ContextValues
from app.utility.crud_auth import CRUD_AUTH_ROLES
from app.utility.database import check_model_difference
from app.utility.error import RYLUpdateNoChange
from app.utility.exceptions import RYLAlreadyExists

app_gd_server = APIBlueprint("gd_server", __name__)


class GDServersQuery(PageSchema):
    search_str = String(required=False, validate=Length(1, 50))


class GDServersPage(Schema):
    servers = List(Nested(GDServerOut))
    pagination = Nested(PaginationSchema)


class GDServersView(MethodView):
    @app_gd_server.output(GDServerOut, status_code=200)
    @app_gd_server.doc("Get GD Server by ID", responses=[404])
    def get(self, server_id):
        server = GDServer.query.filter_by(id=server_id).one_or_none()

        if not server:
            abort(404)

        return server

    @app_gd_server.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["gd_server"].create
    )
    @app_gd_server.input(GDServerIn, location="json")
    @app_gd_server.output(GDServerOut, status_code=201)
    @app_gd_server.doc("Add a GD Server", responses=[409, 500])
    def post(self, json_data):
        current_app.logger.info(f"Request: Add GD server: {json_data}")

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )

            new_server = try_add_gd_server(
                ctx,
                name=json_data["name"],
                description=json_data.get("description"),
                ip=json_data.get("IP"),
                gd_version=json_data.get("GD_version"),
            )

            return new_server

        except RYLAlreadyExists as e:
            current_app.logger.warning(e)
            abort(409, e.message)

        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


class GDServerView(MethodView):
    @app_gd_server.output(GDServerOut, status_code=200)
    @app_gd_server.doc("Get a GD server", responses=[404])
    def get(self, gd_server_id):
        gd_server = GDServer.query.filter_by(id=gd_server_id).one_or_none()

        if not gd_server:
            abort(404)

        return gd_server

    @app_gd_server.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["gd_server"].update
    )
    @app_gd_server.input(GDServerPatch(partial=True), location="json")
    @app_gd_server.output(GDServerOut, status_code=200)
    @app_gd_server.doc("Update a GD Server", responses=[403, 404, 500])
    def patch(self, server_id, json_data):
        current_app.logger.info(
            f"Request: Patch gd server({server_id}): {json_data}"
        )

        server_query = GDServer.query.filter_by(id=server_id)
        server: GDServer = server_query.one_or_none()
        if not server:
            abort(404)

        if not check_model_difference(server, json_data):
            raise RYLUpdateNoChange()

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note", "")
            )
            ctx.set()

            server_query.update(json_data)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)

        return server

    @app_gd_server.auth_required(
        ryl_auth, roles=CRUD_AUTH_ROLES["gd_server"].delete
    )
    @app_gd_server.input(RYLContentIn(partial=True))
    @app_gd_server.output({}, status_code=204)
    @app_gd_server.doc("Delete GD Server", responses=[204, 401, 403, 404])
    def delete(self, server_id, json_data):
        current_app.logger.info(f"Request: Delete gd server: {server_id}")

        server = get_gd_server(server_id)

        if not server:
            abort(404)

        try:
            ctx = ContextValues(
                user_id=current_user.id, note=json_data.pop("note")
            )
            ctx.set()

            db.session.delete(server)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"{type(e).__name__}: {e}")
            abort(500)


app_gd_server.add_url_rule(
    "/v1/gd_servers", view_func=GDServersView.as_view("gd_servers")
)
app_gd_server.add_url_rule(
    "/v1/gd_server/<int:gd_server_id>",
    view_func=GDServerView.as_view("gd_server"),
)
