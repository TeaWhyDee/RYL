from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import ContentBase, ryl_audit
from app.db.models.creator import Creator, Team
from app.db.models.level import Level


@ryl_audit()
class LevelAuthorCreator(ContentBase):
    __tablename__ = "level_author_creators"

    level_id: Mapped[int] = mapped_column(
        "level_id", ForeignKey(Level.id), nullable=False
    )
    creator_id: Mapped[int] = mapped_column(
        "creator_id", ForeignKey(Creator.id), nullable=False
    )

    level = relationship("Level", back_populates="author_creators")
    creator = relationship("Creator", back_populates="level_authorships")

    uix = UniqueConstraint(
        "level_id", "creator_id", name="uix_level_creator_author"
    )

    def __init__(self, level_id: int, creator_id: int):
        self.level_id = level_id
        self.creator_id = creator_id


@ryl_audit()
class LevelAuthorTeam(ContentBase):
    __tablename__ = "level_author_teams"

    level_id: Mapped[int] = mapped_column(
        "level_id", ForeignKey(Level.id), nullable=False
    )
    team_id: Mapped[int] = mapped_column(
        "team_id", ForeignKey(Team.id), nullable=False
    )

    level = relationship("Level", back_populates="author_teams")
    team = relationship("Team", back_populates="level_authorships")

    uix = UniqueConstraint("level_id", "team_id", name="uix_level_team_author")

    def __init__(self, level_id: int, team_id: int):
        self.level_id = level_id
        self.team_id = team_id
