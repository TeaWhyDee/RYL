from dataclasses import dataclass
import os
import enum

from sqlalchemy import Boolean, Integer, String, Enum, ForeignKey, Sequence
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import db


class UserType(enum.Enum):
    normal = "normal"
    moderator = "moderator"
    admin = "admin"
    # banned = "banned"


class User(db.Model):
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    password: Mapped[str] = db.Column(db.String(80))

    public_id: Mapped[int] = db.Column(db.String(50), unique=True)
    username: Mapped[str] = db.Column(db.String(100))
    email: Mapped[str] = db.Column(db.String(70), unique=True)

    user_type = db.Column(db.Enum(UserType), default=UserType.normal)
    is_banned = db.Column(db.Boolean)


class LevelLength(enum.Enum):
    tiny = "tiny"
    short = "short"
    medium = "medium"
    long = "L"
    XL = "XL"
    XXL = "XXL"


class LevelType(enum.Enum):
    level = "level"
    layout = "layout"
    challenge = "challenge"
    minigame = "minigame"


class LevelRating(enum.Enum):
    unrated = "unrated"
    rated = "rated"
    featured = "featured"
    epic = "epic"
    mythic = "mythic"


class Creator(db.Model):
    id = mapped_column(Integer, primary_key=True)

    name = mapped_column(String(50))  # USED IN URL
    # display_name
    # cached genres, roles, description, links, picture


class Team(db.Model):
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(50))  # USED IN URL
    # display_name
    # cached genres, roles


class Level(db.Model):
    id = mapped_column(Integer, primary_key=True)

    # == In-game Info ==
    GD_id: Mapped[int] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String(50))  # USED IN URL
    # CACHED GD account, null ONLY if level is not published
    GD_publisher: Mapped[str] = mapped_column(
        String, nullable=True
    )
    # todo: difficulty, likes, dislikes.

    # == website info ==
    author_host: Mapped[int] = mapped_column("creator_id", ForeignKey(Creator.id))
    author_team: Mapped[int] = mapped_column(
        "team_id", ForeignKey(Team.id), nullable=True
    )
    average_rating: Mapped[int] = mapped_column(Integer, nullable=True)

    is_megacollab: Mapped[bool] = mapped_column(Boolean, default=False)
    level_type: Mapped[LevelType] = mapped_column(
        Enum(LevelType), default=LevelType.level
    )
    length: Mapped[LevelLength] = mapped_column(
        Enum(LevelLength), default=LevelLength.long
    )
    rating: Mapped[LevelRating] = mapped_column(
        Enum(LevelRating), default=LevelRating.featured
    )
    
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return f'<Level {self.name!r}>'


class LevelCreatorRole(enum.Enum):
    host = "host"
    coauthor = "coauthor"
    gameplay = "gameplay"
    decoration = "decoration"
    fx = "fx"
    art = "art"
    background = "background"
    structuring = "structuring"
    engineer = "engineer"


class LevelCreator(db.Model):
    id = mapped_column(Integer, primary_key=True)

    level_id = mapped_column("level_id", ForeignKey(Level.id))
    creator_id = mapped_column("creator_id", ForeignKey(Creator.id))
    creator_role = mapped_column(Enum(LevelCreatorRole))


# GD related stuff (synced with GD servers)
class GD_Account(db.Model):
    id = mapped_column(Integer, primary_key=True)
    GD_id = mapped_column(Integer)

    username = mapped_column(String)





# import jwt
# from datetime import datetime, timedelta
# from werkzeug.security import generate_password_hash, check_password_hash


# class User2(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(200))
#     role = db.Column(db.String(20), default='user')
#
#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)
#
#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)
#
#     def generate_jwt(self, token_type='access'):
#         """Generate JWT token with expiration"""
#         expiration = (
#             timedelta(seconds=int(os.getenv('JWT_ACCESS_EXP')))
#             if token_type == 'access'
#             else timedelta(seconds=int(os.getenv('JWT_REFRESH_EXP')))
#         )
#
#         payload = {
#             'sub': self.id,
#             'email': self.email,
#             'role': self.role,
#             'type': token_type,
#             'exp': datetime.utcnow() + expiration
#         }
#         return jwt.encode(
#             payload,
#             os.getenv('SECRET_KEY'),
#             algorithm='HS256'
#         )
