from apiflask import APIBlueprint, abort
from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import jwt_required

# from app.utility.auth import auth
from app.db.database import db
from app.logic.import_data import import_demonlist_json
from app.utility.auth import auth
from app.schemas.level import LevelOutExtra

app_util = APIBlueprint("util", __name__)


@app_util.post("/upd_demonlist")
@app_util.output(LevelOutExtra)
@app_util.doc(summary="Get featured levels from demonlist", description="")
@app_util.auth_required(auth)
def upd_demonlist():
    level = import_demonlist_json()

    return level
