from apiflask import Schema
from apiflask.fields import String, Boolean
from apiflask.validators import Length
from marshmallow.validate import Email

# from app.schemas import RYLOutSchema


class UserIn(Schema):
    username = String(required=True, validate=Length(3, 20))
    password = String(required=True, validate=Length(8, 30))
    email = String(required=True, validate=Email())


class UserOut(Schema):
    username = String()
    user_type = String()
    is_banned = Boolean()
    is_deleted = Boolean()


class UserLogin(Schema):
    username = String(required=True)
    password = String(required=True)
