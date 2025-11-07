from apiflask import Schema
from apiflask.fields import Integer, String, Enum, Boolean

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
    user_type = String()


class UserLogin(Schema):
    username = String()
    password = String()
