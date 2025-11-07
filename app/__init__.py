import os

# from authlib.integrations.flask_client import OAuth
from apiflask import APIFlask
from dotenv import load_dotenv
from flask import render_template
from flask_migrate import Migrate
from sqlalchemy_declarative_extensions import register_sqlalchemy_events
from werkzeug.middleware.proxy_fix import ProxyFix

from app.db.database import Base, db
from app.db.models.user import User
from app.routes.auth import app_auth
from app.routes.creator import app_creator
from app.routes.credit import app_credit
from app.routes.level import app_level
from app.routes.test import app_test
from app.routes.utility import app_util
from app.utility.auth import jwt_manager

ryl_domain = "ryl.dev"

load_dotenv()


def create_app(test_config=None):
    app = APIFlask(
        __name__,
        instance_relative_config=True,
        # docs_ui="redoc"
    )
    app.servers = [
        {
            "name": "Production Server",
            "url": "https://ryl.teawide.xyz/",
        },
        {
            "name": "Local Server",
            "url": "http://127.0.0.1:5000/",
        },
    ]

    app.secret_key = "asdjb2p3;9urfehbvp984hf;"  # TODO: CHANGE
    os.makedirs(app.instance_path, exist_ok=True)
    app.wsgi_app = ProxyFix(app.wsgi_app)  # for nginx

    # == config ==
    app.config.from_object("app.config.dev")

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    # == init ==
    db.init_app(app)
    jwt_manager.init_app(app)

    migrate = Migrate(app, db)
    # _ = Swagger(app, template_file="openapi3.yml")

    with app.app_context():
        metadata = Base.metadata
        register_sqlalchemy_events(metadata, functions=True, triggers=True)

        db.create_all()

        existing_system_user = User.query.filter_by(username="system").first()

        if not existing_system_user:
            sys_user = User(
                username="system",
                password="a8sf7-a8sd7fa089sd7f09a8s7df",
                email=f"system@{ryl_domain}",
            )
            db.session.add(sys_user)
            db.session.commit()

        if app.config["DEBUG"]:
            existing_user = User.query.filter_by(username="string").first()

            if not existing_user:
                new_user = User(
                    username="string",
                    password="string",
                    email="string",
                )
                db.session.add(new_user)
                db.session.commit()

    # == ROUTES ==
    app.register_blueprint(app_test)
    app.register_blueprint(app_auth)
    app.register_blueprint(app_level)
    app.register_blueprint(app_creator)
    app.register_blueprint(app_util)
    app.register_blueprint(app_credit)

    @app.get("/signup")
    def signup_page():
        return render_template("register.html")

    @app.get("/login")
    def login_page():
        return render_template("login.html")

    @app.get("/")
    def index_page():
        return render_template("levels.html")

    @app.get("/creators")
    def creators_page():
        return render_template("creators.html")

    @app.get("/levels")
    def levels_page():
        return render_template("levels.html")

    @app.get("/layouts")
    def layouts_page():
        return render_template("layouts.html")

    @app.get("/add")
    def add_level_page():
        return render_template("add_level.html")

    @app.get("/creator/<string:creator_url_name>")
    def creator_page(creator_url_name):
        return render_template("creator.html")

    @app.get("/level/<string:level_url_name>")
    def level_page(level_url_name):
        return render_template("level.html")

    # Created app:
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, use_debugger=False, use_reloader=False)
