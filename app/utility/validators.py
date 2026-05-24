from apiflask.validators import Validator
from flask_jwt_extended import current_user
from marshmallow import ValidationError

from app.db.models.user import UserRole


class Authorized(Validator):
    """
    :param auth_level: Minimum authorization level to use feature.

    :param error: Error message to raise in case of a validation error.
    """

    message_not_authorized = "Not authorized. Required auth level: {auth_level}"

    def __init__(
        self,
        auth_level: UserRole,
        *,
        error: str | None = None,
    ):
        self.auth_level = auth_level
        self.error = error

    def _repr_args(self) -> str:
        return f"auth_level={self.auth_level!r}"

    def _format_error(self, value: str) -> str:
        return self.error or self.message_not_authorized.replace(
            "{auth_level}", str(self.auth_level.name)
        )

    def __call__(self, value: str) -> str:
        message = self._format_error(value)

        if current_user.user_role.value < self.auth_level.value:
            raise ValidationError(message)

        return value
