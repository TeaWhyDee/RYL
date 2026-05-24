from apiflask import APIBlueprint, abort
from flask import current_app, jsonify, make_response, request
from flask_jwt_extended import (
    create_access_token,
    current_user,
    get_jwt_identity,
)

from app import routes
from app.db.database import db
from app.db.models.user import User
from app.db.services.user import try_create_user
from app.schemas.user import UserIn, UserLogin, UserOut
from app.utility.auth import ryl_auth
from app.utility.context import ContextValues

app_auth = APIBlueprint("auth", __name__)

# TODO:
# https://flask-security-too.readthedocs.io/en/stable/installation.html


@app_auth.post("/v1/auth/signup")
@app_auth.input(UserIn)
@app_auth.output(UserOut)
def register(json_data):
    username = json_data.get("username")
    password = json_data.get("password")
    email = json_data.get("email")

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        abort(401, "User already exists. Please login.")

    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        abort(400, "Email already used")

    # try creating new user
    try:
        cxt = ContextValues(user_id=1, note="Registration")
        new_user = try_create_user(cxt, username, password, email)

        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        abort(500, f"message: {e}")

    return new_user


@app_auth.post("/v1/auth/login")
@app_auth.input(UserLogin)
@app_auth.output(UserOut)
def login(json_data):
    # response = make_response({"jwt_token": token})
    # response.set_cookie("jwt_token", token, httponly=True, path="/")

    current_app.logger.warning(json_data)

    username = json_data.get("username")
    password = json_data.get("password")

    user = User.query.filter_by(username=username).one_or_none()
    if not user or not user.check_password(password):
        return jsonify("Wrong username or password"), 401

    # sqlalchemy user object as payload
    access_token = create_access_token(identity=user)
    return jsonify(access_token=access_token)


@app_auth.get("/v1/whoami/")
@app_auth.output(UserOut)
@app_auth.auth_required(ryl_auth)
@app_auth.doc(
    responses={
        200: {
            "description": "Returns User Schema",
        }
    }
)
def whoami():
    return current_user
