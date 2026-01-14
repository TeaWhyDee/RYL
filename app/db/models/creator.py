from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import ContentBase, ryl_audit
from app.utility.util import sanitize_url

#
# TODO: rating cache mixin
# class AuthorMixin


@ryl_audit()
class Creator(ContentBase):
    __tablename__ = "creators"

    display_name: Mapped[str] = mapped_column(String(50), nullable=False)
    url_name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )

    clan: Mapped[str] = mapped_column(String(50), nullable=True)
    about: Mapped[str] = mapped_column(String(2000), nullable=True)
    # cached genres, roles;  links, picture

    @hybrid_property
    def url(self) -> str:
        return f"/creator/{self.url_name}"

    credits = relationship("LevelCredit", back_populates="creator")
    level_authorships = relationship(
        "LevelAuthorCreator", back_populates="creator"
    )
    team_memberships = relationship("TeamMember", back_populates="creator")

    def __init__(self, name: str):
        self.display_name = name
        self.url_name = sanitize_url(name)


@ryl_audit()
class Team(ContentBase):
    __tablename__ = "teams"

    display_name: Mapped[str] = mapped_column(String(50), nullable=False)
    url_name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )

    about: Mapped[str] = mapped_column(String(2000))

    # === relationships ===
    level_authorships = relationship("LevelAuthorTeam", back_populates="team")
    memberships = relationship("TeamMember", back_populates="team")

    @hybrid_property
    def url(self) -> str:
        return f"/team/{self.url_name}"

    # display_name
    # cached genres, roles

    def __init__(self, name: str):
        self.display_name = name
        self.url_name = sanitize_url(name)


@ryl_audit()
class TeamMember(ContentBase):
    __tablename__ = "team_memberships"
    # one creator can be in the same team twice, if they quit and rejoin a later

    creator_id: Mapped[int] = mapped_column(
        ForeignKey(Creator.id), nullable=False
    )
    team_id: Mapped[int] = mapped_column(ForeignKey(Team.id), nullable=False)

    membership_start: Mapped[date] = mapped_column(Date, nullable=True)
    membership_end: Mapped[date] = mapped_column(Date, nullable=True)
    is_owner: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    creator = relationship("Creator", back_populates="team_memberships")
    team = relationship("Team", back_populates="memberships")

    def __init__(self, creator_id: int, team_id: int, is_owner: bool):
        self.creator_id = creator_id
        self.team_id = team_id
        self.is_owner = is_owner


# GD related stuff (synced with GD servers)
@ryl_audit()
class GD_Account(ContentBase):
    __tablename__ = "GD_account"

    GD_id = mapped_column(Integer)

    username = mapped_column(String)
