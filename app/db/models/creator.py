from typing import Optional

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import CompletenessStatus, ContentBase, ryl_audit
from app.utility.util import sanitize_for_url


@ryl_audit()
class Creator(ContentBase):
    __tablename__ = "creators"

    display_name = mapped_column(String(50))
    url_name = mapped_column(String(60), unique=True)
    # clan = mapped_column(String(50))

    description = mapped_column(String(5000))
    # cached genres, roles, description, links, picture

    completeness_status: Mapped[CompletenessStatus] = mapped_column(
        Enum(
            CompletenessStatus,
            nullable=False,
        ),
        default=CompletenessStatus.imported_GD,
    )

    # relationships
    team_memberships = relationship("TeamMember", back_populates="creator")

    # levels = relationship("Level", back_populates="creator")
    credits = relationship("LevelCredit", back_populates="creator")
    level_authorships = relationship(
        "LevelAuthorship", back_populates="creator"
    )

    def __init__(
        self,
        display_name: str,
        url_name: str,
        completeness_status: CompletenessStatus,
        description: Optional[str] = None,
    ):
        self.completeness_status = completeness_status
        self.display_name = display_name
        self.url_name = url_name
        self.description = description
