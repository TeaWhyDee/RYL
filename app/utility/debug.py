from app.db.database import CompletenessStatus, db
from app.db.models.creator import Creator
from app.db.models.genre import Genre
from app.db.models.team import Team
from app.db.models.user import User, UserRole
from app.db.services.creator import try_add_creator
from app.db.services.genre import try_add_genre
from app.db.services.team import try_add_team
from app.utility.context import ContextValues


def add_debug_user(username: str, user_role: UserRole):
    existing_user = User.query.filter_by(username=username).first()

    if not existing_user:
        new_user = User(
            username=username,
            password=username,
            email=username,
            user_role=user_role,
        )
        db.session.add(new_user)
        db.session.commit()


def add_debug_team(name: str):
    try:
        existing_team = Team.query.filter_by(display_name=name).one_or_none()

        if not existing_team:
            ctx = ContextValues(user_id=1, note="debug")

            try_add_team(
                ctx,
                name=name,
                completeness_status=CompletenessStatus.mod_approved,
                description=f"{name} description",
            )
    except:
        pass


def add_debug_genre(name: str):
    try:
        existing = Genre.query.filter_by(display_name=name).one_or_none()

        if not existing:
            ctx = ContextValues(user_id=1, note="debug")

            try_add_genre(
                ctx,
                name=name,
                description=f"{name} description",
            )
    except:
        pass


def add_debug_creator(name: str):
    try:
        existing_creator = Creator.query.filter_by(
            display_name=name
        ).one_or_none()

        if not existing_creator:
            ctx = ContextValues(user_id=1, note="debug")

            try_add_creator(
                ctx,
                name=name,
                completeness_status=CompletenessStatus.mod_approved,
                description=f"{name} description",
            )
    except:
        pass
