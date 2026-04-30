import enum

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base, ContentBase, db, ryl_audit
from app.db.models.creator import Creator
from app.db.models.credit import LevelCreatorRole
from app.db.models.level import Level


@ryl_audit()
class LevelAuthor(ContentBase):
    # Collaborators of a level.
    # Additional creator credit for a level.
    __tablename__ = "level_credits"

    level_id: Mapped[int] = mapped_column("level_id", ForeignKey(Level.id))
    creator_id: Mapped[int] = mapped_column(
        "creator_id", ForeignKey(Creator.id)
    )
    team_id: Mapped[int] = mapped_column("creator_id", ForeignKey(Creator.id))

    level = relationship("Level", back_populates="credits")
    creator = relationship("Creator", back_populates="credits")

    def __init__(
        self, level_id: int, creator_id: int, creator_role: LevelCreatorRole
    ):
        self.level_id = level_id
        self.creator_id = creator_id
        self.creator_role = creator_role
