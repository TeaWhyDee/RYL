import enum
from typing import Optional

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base, CompletenessStatus, ContentBase, db, ryl_audit
from app.db.models.creator import Creator
from app.db.models.level import Level
from app.utility.util import sanitize_for_url


@ryl_audit()
class Team(ContentBase):
    # GD Team like Cherry team
    # Can have associated GD accounts
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

    def __init__(
        self,
        name: str,
        completeness_status: CompletenessStatus,
        description: Optional[str],
    ):
        self.url_name = sanitize_for_url(name)
        self.display_name = name
        self.description = description
        self.completeness_status = completeness_status

    def __repr__(self):
        return f"<Team {self.id}:{self.url_name!r}({self.display_name})>"
