from apiflask import APIBlueprint, abort
from flask import current_app
from flask.views import MethodView

# from app.utility.auth import auth
from app.db.database import db
from app.utility.auth import auth

app_test = APIBlueprint("test", __name__)


@app_test.route("/ping")
@app_test.doc(summary='Say pong', description='Some description')
def ping():
    return "pong"
