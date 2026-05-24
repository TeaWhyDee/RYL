from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import ContentBase, ryl_audit


@ryl_audit()
class Genre(ContentBase):
    """A genre/category for levels."""

    __tablename__ = "genres"

    name: Mapped[str] = mapped_column(String, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    url_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    # relationships
    level_genres = relationship("LevelGenre", back_populates="genre")

    def __init__(
        self,
        name: str,
        display_name: str,
        url_name: str,
        description: Optional[str] = None,
    ):
        self.name = name
        self.display_name = display_name
        self.url_name = url_name
        self.description = description
