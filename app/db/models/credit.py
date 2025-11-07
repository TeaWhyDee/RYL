import enum

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base, ContentBase, db, ryl_audit
from app.db.models.creator import Creator
from app.db.models.level import Level


class LevelCreatorRole(enum.Enum):
    host = "host"
    collaborator = "collaborator"  # generic collaborator
    gameplay = "gameplay"
    decoration = "decoration"
    fx = "fx"
    art = "art"
    background = "background"
    structuring = "structuring"
    engineer = "engineer"
    playtester = "playtester"
    verifier = "verifier"


@ryl_audit()
class LevelCredit(ContentBase):
    # Collaborators of a level.
    # Additional creator credit for a level.
    __tablename__ = "level_credits"

    level_id = mapped_column("level_id", ForeignKey(Level.id))
    creator_id = mapped_column("creator_id", ForeignKey(Creator.id))
    creator_role = mapped_column(Enum(LevelCreatorRole))

    level = relationship("Level", back_populates="credits")
    creator = relationship("Creator", back_populates="credits")

    def __init__(
        self, level_id: int, creator_id: int, creator_role: LevelCreatorRole
    ):
        self.level_id = level_id
        self.creator_id = creator_id
        self.creator_role = creator_role
