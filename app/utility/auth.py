from apiflask import HTTPTokenAuth
from flask import current_app
from flask_jwt_extended import (
    JWTManager,
    current_user,
    get_jwt_identity,
    verify_jwt_in_request,
)
from sqlalchemy_declarative_extensions.audit import set_context_values

from app.db.database import db
from app.db.models.user import User

#
# == APIFlask Auth ==
#
auth = HTTPTokenAuth()


@auth.verify_token
def verify_token(token):
    # This call to flask-jwt-extended:
    # - sets necessary variables
    # - verifies the jwt
    # - throws exceptions in case of failed verification
    verify_jwt_in_request(
        optional=False,
        fresh=False,
        refresh=False,
        locations=None,
        verify_type=True,
        skip_revocation_check=False,
    )

    # if ret:
    #     jwt_header, jwt_data = ret

    try:
        user_identity = get_jwt_identity()
        # TODO: Can be optimized (avoid making so many calls)
        # Set current user for SQLA-audit
        set_context_values(db.session, user_id=current_user.id)
        return user_identity

    except Exception as e:
        current_app.logger.warning(e)
        return None


# == Flask JWT Extended ==
# Documentation:
# https://flask-jwt-extended.readthedocs.io/en/stable/basic_usage.html
#
# Optional Protection:
# https://flask-jwt-extended.readthedocs.io/en/stable/optional_endpoints.html
#
# Configuration:
# https://flask-jwt-extended.readthedocs.io/en/stable/options.html
#
# Refreshing:
# https://flask-jwt-extended.readthedocs.io/en/stable/refreshing_tokens.html
#
# Revoking:
# https://flask-jwt-extended.readthedocs.io/en/stable/blocklist_and_token_revoking.html
jwt_manager = JWTManager()


@jwt_manager.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt_manager.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]

    if current_app.config["DEBUG"]:
        current_app.logger.warning(jwt_data)

    return User.query.filter_by(id=identity).one_or_none()
