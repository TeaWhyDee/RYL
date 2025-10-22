import os
import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from dotenv import load_dotenv
from flasgger import Swagger
# from authlib.integrations.flask_client import OAuth
from flask import Flask, jsonify, make_response, render_template, request
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash

from app.db.database import db
from app.db.models import Creator, Level, User, UserType
from app.routes.test import routes_test

load_dotenv()


def get_jwt_token(user: User, secret_key: str):
    # https://pyjwt.readthedocs.io/en/latest/usage.html#encoding-decoding-tokens-with-hs256
    token = jwt.encode(
        {
            "public_id": user.public_id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
        },
        secret_key,
        algorithm="HS256",
    )

    return token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("jwt_token")

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=data["public_id"]).first()
        except:
            return jsonify({"message": "Token is invalid!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


def token_optional(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("jwt_token")

        current_user = None

        if token:
            try:
                data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
                current_user = User.query.filter_by(public_id=data["public_id"]).first()
            except:
                pass

        return f(current_user, *args, **kwargs)

    return decorated


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = "asdjb2p3;9urfehbvp984hf;"  # TODO: CHANGE
    os.makedirs(app.instance_path, exist_ok=True)
    # app.wsgi_app = ProxyFix(app.wsgi_app)  # for nginx

    # config
    app.config.from_object("app.config.dev")

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    # init
    db.init_app(app)
    _ = Migrate(app, db)
    _ = Swagger(app, template_file="openapi3.yml")
    # swagger = Swagger(app, template={ "swagger": "3.0", "openapi": '3.0.2', })

    with app.app_context():
        db.create_all()

    # ROUTES
    app.register_blueprint(routes_test)

    @app.post("/hello")
    def hello():
        """asd
        ---
        parameters:
        - name: param
          type: object
          in: body
          required: true
          properties:
            param:
                type: string
        responses:
            200:
                description: asdasd
        """
        param = request.json.get("param")
        return jsonify({"DEBUG": app.config["DEBUG"], "param": param})

    @app.get("/signup")
    def signup_page():
        return render_template("register.html")

    @app.get("/login")
    def login_page():
        return render_template("login.html")

    @app.post("/v1/auth/signup")
    def register():
        """
        signup
        ---
        tags: ['auth']
        requestBody:
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            username:
                                type: string
                            email:
                                type: string
                            password:
                                type: string
        responses:
            200:
                description: Success

        """
        username = request.json.get("username")
        email = request.json.get("email")
        password = request.json.get("password")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({"message": "User already exists. Please login."}), 400

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({"message": "Email already used."}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(
            public_id=str(uuid.uuid4()),
            username=username,
            email=email,
            password=hashed_password,
            user_type=UserType.normal,
        )

        db.session.add(new_user)
        db.session.commit()

        return {"message": "Success"}, 200

    @app.post("/v1/auth/login")
    def login():
        """
        login
        ---
        tags: ['auth']
        requestBody:
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            username:
                                type: string
                            password:
                                type: string
        responses:
            200:
                description: Success
                headers:
                    Set-Cookie:
                        schema:
                            type: string
                            example: jwt_token=abcde12345; Path=/; HttpOnly
        """
        username = request.json.get("username")
        password = request.json.get("password")
        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({"message": "Invalid email or password"}), 401

        token = get_jwt_token(user, app.config["SECRET_KEY"])

        response = make_response({"jwt_token": token})
        response.set_cookie("jwt_token", token, httponly=True, path="/")

        return response

    @app.post("/v1/whoami/")
    @token_required
    def whoami(current_user):
        """
        get username
        ---
        security:
        - cookieAuth: []
        responses:
            200:
                schema:
                    type: object
                    properties:
                        username:
                            type: string
        """
        return jsonify({"username": current_user.username}), 200

    @app.get("/v1/creator/<id>")
    @token_required
    def get_creator(current_user, id):
        """
        get a creator
        ---
        tags: ['mod']
        parameters:
              - in: path
                name: id
                schema:
                    type: integer
        responses:
            200:
                schema:
                    type: object
                    properties:
                        username:
                            type: string
            404:
                schema:
                    type: object
        """

        try:
            creator = Creator.query.filter_by(id=id).first_or_404()
        except Exception as e:
            app.logger.warning(msg=repr(e))
            return jsonify({"message": "Couldn't find creator."}), 401

        return jsonify(creator.name, creator.id), 200

    @app.post("/v1/add_creator")
    @token_required
    def add_creator(current_user):
        """
        add a creator
        ---
        tags: ['mod']
        requestBody:
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            name:
                                type: string
        responses:
            200:
                schema:
                    type: object
                    properties:
                        username:
                            type: string
            401:
                schema:
                    type: object
        """

        try:
            name = request.json.get("name")

            new_creator = Creator(name=name)

            db.session.add(new_creator)
            db.session.commit()
        except Exception as e:
            app.logger.warning(msg=repr(e))
            return jsonify({"message": "Couldn't add creator."}), 401

        return jsonify({"name": name, "id": new_creator.id}), 200

    @app.get("/v1/level/<id>")
    @token_optional
    def get_level(current_user, id):
        """
        get a level
        ---
        tags: ['mod']
        parameters:
              - in: path
                name: id
                schema:
                    type: integer
        responses:
            200:
                schema:
                    type: object
                    properties:
                        level:
                            type: string
            404:
                schema:
                    type: object
        """

        try:
            level = Level.query.filter_by(id=id).first_or_404()
        except Exception as e:
            app.logger.warning(msg=repr(e))
            return jsonify({"message": "Couldn't find level."}), 401

        return jsonify(level), 200

    @app.post("/v1/add_level")
    @token_required
    def add_level(current_user):
        """
        add a level
        ---
        tags: ['mod']
        requestBody:
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            name:
                                type: string
                            host_id:
                                type: integer
        responses:
            200:
                schema:
                    type: object
                    properties:
                        username:
                            type: string
            401:
                schema:
                    type: object
        """

        try:
            name: str = request.json.get("name")
            host_id: int = request.json.get("host_id")

            new_level = Level(name=name, author_host=host_id)

            db.session.add(new_level)
            db.session.commit()

        except Exception as e:
            app.logger.warning(msg=repr(e))
            return jsonify({"message": "Couldn't add level."}), 40

        # return jsonify({new_level.id, new_level.author_host, new_level.name}), 200
        return (
            jsonify(
                {
                    "id": new_level.id,
                    "host_id": new_level.author_host,
                    "name": new_level.name,
                }
            ),
            200,
        )

    # Created app:
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

    # @app.route('/auth/oauth2/google/')
    # def google():
    #
    #     # Google Oauth Config
    #     # Get client_id and client_secret from environment variables
    #     # For developement purpose you can directly put it
    #     # here inside double quotes
    #     GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    #     GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    #     GOOGLE_DISCOVERY_URL = (
    #         "https://accounts.google.com/.well-known/openid-configuration"
    #     )
    #
    #     CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    #     oauth.register(
    #         name='google',
    #         client_id=GOOGLE_CLIENT_ID,
    #         client_secret=GOOGLE_CLIENT_SECRET,
    #         server_metadata_url=CONF_URL,
    #         client_kwargs={
    #             'scope': 'openid email profile'
    #         }
    #     )
    #
    #     # Redirect to google_auth function
    #     redirect_uri = url_for('google_auth', _external=True)
    #     return oauth.google.authorize_redirect(redirect_uri)
    #
    # @app.route('/google/auth/')
    # def google_auth():
    #     token = oauth.google.authorize_access_token()
    #     user = oauth.google.parse_id_token(token)
    #     print(" Google User ", user)
    #     return redirect('/')
