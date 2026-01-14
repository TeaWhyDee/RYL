import enum

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import ContentBase, ryl_audit
from app.db.models.creator import Creator
from app.db.models.level import Level


class LevelCreditRole(enum.Enum):
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

    level_id: Mapped[int] = mapped_column(
        "level_id", ForeignKey(Level.id), nullable=False
    )
    creator_id: Mapped[int] = mapped_column(
        "creator_id", ForeignKey(Creator.id), nullable=False
    )
    creator_role: Mapped[LevelCreditRole] = mapped_column(
        Enum(LevelCreditRole), nullable=False
    )

    level = relationship("Level", back_populates="credits")
    creator = relationship("Creator", back_populates="credits")

    def __init__(
        self, level_id: int, creator_id: int, creator_role: LevelCreditRole
    ):
        self.level_id = level_id
        self.creator_id = creator_id
        self.creator_role = creator_role
