import enum
import uuid
from dataclasses import dataclass

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.db.database import Base, db
from app.utility.util import sanitize_for_url


class UserType(enum.Enum):
    normal = 2
    helper = 5
    moderator = 7
    admin = 10
    system = 10


class User(Base):
    __tablename__ = "users"

    # public_id: Mapped[str] = mapped_column(String(50), unique=True)
    username: Mapped[str] = mapped_column(String(100))
    display_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(70), unique=True)
    password: Mapped[str] = mapped_column(String(200))

    is_banned: Mapped[bool] = mapped_column(Boolean)
    is_deleted: Mapped[bool] = mapped_column(Boolean)
    user_type: Mapped[UserType] = mapped_column(Enum(UserType))

    # == Preferences ==
    # preferences = relationship(
    #     "UserPreferences", back_populates="user", uselist=False
    # )

    def user_type_change(self, new_type: UserType):
        self.user_type = new_type

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __init__(
        self,
        username: str,
        password: str,
        email: str,
        user_type: UserType = UserType.normal,
    ):
        """
        Use services/try_create_user for user creation instead.
        Creates user with default values and sanitized username.
        Does NOT throw Exceptions in case of bad values.
        """
        hashed_password = generate_password_hash(password)

        # self.public_id = str(uuid.uuid4())
        self.username = sanitize_for_url(username)
        self.display_name = username
        self.email = email
        self.password = hashed_password

        self.is_banned = False
        self.is_deleted = False
        self.user_type = user_type

    def __repr__(self):
        return f"<User {self.id}:{self.username!r}>"
