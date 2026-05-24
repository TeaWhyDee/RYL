from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import CompletenessStatus, ContentBase, ryl_audit
from app.utility.util import sanitize_for_url


@ryl_audit()
class Team(ContentBase):
    """
    GD Team like Cherry team.
    Can have associated GD accounts.
    """

    __tablename__ = "teams"

    url_name = mapped_column(String(60), unique=True)
    display_name = mapped_column(String(50), unique=True)

    description = mapped_column(String(5000))

    # member count?
    # average score?

    completeness_status: Mapped[CompletenessStatus] = mapped_column(
        Enum(
            CompletenessStatus,
            nullable=False,
        ),
        default=CompletenessStatus.imported_GD,
    )

    team_memberships = relationship("TeamMember", back_populates="team")

    def __init__(
        self,
        url_name: str,
        display_name: str,
        completeness_status: CompletenessStatus,
        description: str,
    ):
        self.url_name = url_name
        self.display_name = display_name
        self.description = description
        self.completeness_status = completeness_status

    def __repr__(self):
        return f"<Team {self.id}:{self.url_name!r}({self.display_name})>"
