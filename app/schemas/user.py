from apiflask import Schema
from apiflask.fields import Boolean, Enum, Integer, String

# ===
# Change default response format
# ===
# class BaseResponse(Schema):
#     data = Field()  # the data key
#     message = String()
#     code = Integer()

# app.config['BASE_RESPONSE_SCHEMA'] = BaseResponse


class UserIn(Schema):
    username = String()
    password = String()
    email = String()


class UserOut(Schema):
    public_id = String()
    username = String()
    display_name = String()
    is_banned = Boolean()
    user_type = String()


# only passed on login
class UserLogin(Schema):
    username = String()
    password = String()
