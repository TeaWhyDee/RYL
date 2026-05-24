import json
import os

# from authlib.integrations.flask_client import OAuth
from apiflask import APIFlask
from dotenv import load_dotenv
from flask import render_template
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
from sqlalchemy_declarative_extensions import register_sqlalchemy_events
from werkzeug.middleware.proxy_fix import ProxyFix

from app.db.database import Base, CompletenessStatus, db
from app.db.models.gd_server import GDServer
from app.db.models.level import GDVersion
from app.db.models.team import Team
from app.db.models.user import User, UserRole
from app.db.services.gd_server import try_add_gd_server
from app.logic.data.import_data import (
    import_demonlist_json,
    import_top50_likes,
    import_top500_likes,
)
from app.logic.data.retreive_data import augment_level, retreive_gdhistory
from app.routes.auth import app_auth
from app.routes.creator import app_creator
from app.routes.credit import app_credit
from app.routes.gd_account import app_gd_account
from app.routes.gd_server import app_gd_server
from app.routes.genre import app_genre
from app.routes.level import app_level
from app.routes.level_authorship import app_level_authorship
from app.routes.level_genre import app_level_genre
from app.routes.level_upload import app_level_upload
from app.routes.team import app_team
from app.routes.team_member import app_team_member
from app.routes.test import app_test
from app.routes.utility import app_util
from app.utility.auth import jwt_manager
from app.utility.context import ContextValues
from app.utility.debug import add_debug_genre, add_debug_team, add_debug_user

ryl_domain = "ryl.dev"

load_dotenv()


def ryl_init_db(app: APIFlask):
    ctx = ContextValues(user_id=1, note="db init")

    #
    # System User
    #
    existing_system_user = User.query.filter_by(username="system").first()
    if existing_system_user:
        assert existing_system_user.id == 1
    else:
        sys_user = User(
            username="system",
            password="a8sf7-a8sd7fa089sd7f09a8s7df",
            email=f"system@{ryl_domain}",
        )
        ctx.set()
        db.session.add(sys_user)
        db.session.commit()

    #
    # Defaults
    #
    existing_team = Team.query.filter_by(id=1).first()
    if existing_team:
        assert existing_team.url_name == "unknown-team"
    else:
        unk_team = Team(
            display_name="Unknown Team",
            url_name="unknown-team",
            completeness_status=CompletenessStatus.mod_approved,
            description="Placeholder team for unknwon/missing teams.",
        )
        ctx.set()
        db.session.add(unk_team)
        db.session.commit()

    existing_gd_server = GDServer.query.filter_by(id=1).first()
    if existing_gd_server:
        assert existing_gd_server.url_name == "official"
    else:
        gd_server = GDServer(
            display_name="RobTop",
            url_name="official",
            ip="1",
            gd_version=GDVersion.ver22,
        )

        ctx.set()
        db.session.add(gd_server)
        db.session.commit()

    #
    # DEBUG
    #
    if app.config["DEBUG"]:
        add_debug_user("string", UserRole.normal)
        add_debug_user("user", UserRole.normal)
        add_debug_user("helper", UserRole.helper)
        add_debug_user("mod", UserRole.moderator)
        add_debug_user("admin", UserRole.admin)

        add_debug_team("team2")
        add_debug_team("team3")
        add_debug_team("team4")

        add_debug_genre("test genre")

        import_demonlist_json()
        import_demonlist_json()
        import_demonlist_json()
        import_demonlist_json()
        import_demonlist_json()

        # import_top50_likes()
        import_top500_likes()


def create_app(test_config=None):
    app = APIFlask(
        __name__,
        instance_relative_config=True,
        # docs_ui="redoc"
    )

    CORS(
        app,
        resources={
            r"/v1/*": {"origins": ["http://localhost:*", "https://teawide.xyz"]}
        },
    )
    app.config["CORS_HEADERS"] = ["Content-Type", "Accept", "Authorization"]

    app.servers = [
        {
            "name": "Production Server",
            "url": "https://ryl.teawide.xyz/",
        },
        {
            "name": "Local Server",
            "url": "http://localhost:5000/",
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

        # Create DB entries:
        # defaults & necessary for operation
        ryl_init_db(app)

    # == ROUTES ==
    # app.register_blueprint(app_test)
    app.register_blueprint(app_util)
    app.register_blueprint(app_auth)

    # Content
    app.register_blueprint(app_level)
    app.register_blueprint(app_creator)
    app.register_blueprint(app_team)
    app.register_blueprint(app_genre)

    # Associations
    app.register_blueprint(app_credit)
    app.register_blueprint(app_team_member)
    app.register_blueprint(app_level_authorship)
    app.register_blueprint(app_level_genre)

    # GD
    app.register_blueprint(app_gd_server)
    app.register_blueprint(app_gd_account)
    app.register_blueprint(app_level_upload)

    @app.get("/signup")
    def signup_page():
        return render_template("register.html")

    @app.get("/login")
    def login_page():
        return render_template("login.html")

    @app.get("/")
    def index_page():
        return render_template("levels.html")

    # @app.get("/creators")
    # def creators_page():
    #     return render_template("creators.html")
    #
    # @app.get("/levels")
    # def levels_page():
    #     return render_template("levels.html")
    #
    # @app.get("/layouts")
    # def layouts_page():
    #     return render_template("layouts.html")
    #
    # @app.get("/add")
    # def add_level_page():
    #     return render_template("add_level.html")

    # @app.get("/creator/<string:creator_url_name>")
    # def creator_page(creator_url_name):
    #     return render_template("creator.html")
    #
    # @app.get("/level/<string:level_url_name>")
    # def level_page(level_url_name):
    #     return render_template("level.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, use_debugger=False, use_reloader=False)
