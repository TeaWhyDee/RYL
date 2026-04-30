from app.db.models.team import Team
from app.db.models.user import User, UserType
from app.db.database import CompletenessStatus, db
from app.db.services.team import try_add_team
from app.utility.context import ContextValues


def add_debug_user(username: str, user_type: UserType):
    existing_user = User.query.filter_by(username=username).first()

    if not existing_user:
        new_user = User(
            username=username,
            password=username,
            email=username,
            user_type=user_type,
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
                completeness_status=CompletenessStatus.user_edited,
                description=f"{name} description",
            )
    except:
        pass
