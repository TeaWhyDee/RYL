import enum
import uuid
from dataclasses import dataclass

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.db.database import Base, db


class UserType(enum.Enum):
    normal = "normal"
    moderator = "moderator"
    admin = "admin"
    # banned = "banned"


class User(Base):
    __tablename__ = "users"

    password: Mapped[str] = mapped_column(String(200))

    public_id: Mapped[str] = mapped_column(String(50), unique=True)
    username: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(70), unique=True)

    is_banned: Mapped[bool] = mapped_column(Boolean)
    user_type: Mapped[UserType] = mapped_column(Enum(UserType))

    # == Preferences ==
    # preferences = relationship(
    #     "UserPreferences", back_populates="user", uselist=False
    # )

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __init__(self, username: str, password: str, email: str):
        hashed_password = generate_password_hash(password)

        self.public_id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password = hashed_password

        self.is_banned = False
        self.user_type = UserType.normal

    def __repr__(self):
        return f"<Level {self.name!r}>"
