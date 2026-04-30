import enum

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_declarative_extensions.audit import audit

from app.db.database import Base, CompletenessStatus, ContentBase, db, ryl_audit
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

    # levels = relationship("Level", back_populates="creator")
    credits = relationship("LevelCredit", back_populates="creator")

    def __init__(self, name: str):
        self.display_name = name
        self.url_name = sanitize_for_url(name)
