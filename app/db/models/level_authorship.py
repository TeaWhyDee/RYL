from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import ContentBase, ryl_audit
from app.db.models.creator import Creator
from app.db.models.level import Level
from app.db.models.team import Team
from app.utility.exceptions import RYLInternalError


@ryl_audit()
class LevelAuthorship(ContentBase):
    """
    An author of the level (level can have multiple authors).
    EITHER a team or a creator.
    One LeverlAuthorship cannot link BOTH to a team and a creator.
    """

    __tablename__ = "level_authors"

    level_id: Mapped[int] = mapped_column("level_id", ForeignKey(Level.id))
    # Author
    creator_id: Mapped[int] = mapped_column(
        "creator_id", ForeignKey(Creator.id), nullable=True
    )
    team_id: Mapped[int] = mapped_column(
        "team_id", ForeignKey(Team.id), nullable=True
    )

    # TODO
    # author_alias_id

    level = relationship("Level", back_populates="authorships")
    creator = relationship("Creator", back_populates="level_authorships")

    def __init__(
        self, level_id: int, creator_id: Optional[int], team_id: Optional[int]
    ):
        if team_id and level_id:
            raise RYLInternalError(
                "Cannot create level_authorship with both team and creator FK."
            )

        if team_id:
            self.team_id = team_id

        if creator_id:
            self.creator_id = creator_id

        self.level_id = level_id
