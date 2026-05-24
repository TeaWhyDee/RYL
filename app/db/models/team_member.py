import enum
from typing import Optional
from sqlalchemy import Date, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import ContentBase, ryl_audit
from app.db.models.team import Team
from app.db.models.creator import (
    Creator,
)  # Assuming Creator is the user/account model


class TeamRole(enum.Enum):
    creator = 1
    owner = 2
    verifier = 3


@ryl_audit()
class TeamMember(ContentBase):
    """
    Represents a member associated with a specific Team.
    Links a Creator to a Team and defines their role within that team.
    Optionally, can specify join and leave date.
    """

    __tablename__ = "team_members"

    # Attributes
    role: Mapped[TeamRole] = mapped_column(
        SQLEnum(TeamRole), nullable=False, default=TeamRole.creator
    )
    date_joined: Mapped[Date | None] = mapped_column(Date)
    date_left: Mapped[Date | None] = mapped_column(Date, nullable=True)

    # Foreign Keys
    team_id: Mapped[int] = mapped_column(ForeignKey(Team.id), nullable=False)
    creator_id: Mapped[int] = mapped_column(
        ForeignKey(Creator.id), nullable=False
    )

    # Relationships
    team: Mapped["Team"] = relationship(
        "Team", back_populates="team_memberships"
    )
    creator: Mapped["Creator"] = relationship(
        "Creator", back_populates="team_memberships"
    )

    def __init__(
        self,
        team_id: int,
        creator_id: int,
        role: TeamRole = TeamRole.creator,
        date_joined: Optional[Date] = None,
        date_left: Optional[Date] = None,
    ):
        self.team_id = team_id
        self.creator_id = creator_id
        self.role = role
        self.date_joined = date_joined
        self.date_left = date_left

    def __repr__(self):
        return f"<TeamMember {self.id}: CreatorID={self.creator_id}, TeamID={self.team_id}, Role={self.role.name}>"
