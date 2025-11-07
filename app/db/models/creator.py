import enum

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_declarative_extensions.audit import audit

from app.db.database import Base, ContentBase, db, ryl_audit
from app.utility.util import sanitize_url


@ryl_audit()
class Creator(ContentBase):
    __tablename__ = "creators"

    display_name = mapped_column(String(50))
    url_name = mapped_column(String(50), unique=True)
    clan = mapped_column(String(50))

    about = mapped_column(String(1000))
    # cached genres, roles, description, links, picture

    # levels = relationship("Level", back_populates="creator")
    credits = relationship("LevelCredit", back_populates="creator")

    def __init__(self, name: str):
        self.display_name = name
        self.url_name = sanitize_url(name)


@ryl_audit()
class Team(ContentBase):
    __tablename__ = "teams"

    display_name = mapped_column(String(50))
    url_name = mapped_column(String(50), unique=True)
    # name = mapped_column(String(50))  # USED IN URL
    # display_name
    # cached genres, roles


# GD related stuff (synced with GD servers)
@ryl_audit()
class GD_Account(ContentBase):
    __tablename__ = "GD_account"

    GD_id = mapped_column(Integer)

    username = mapped_column(String)
