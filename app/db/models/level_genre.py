from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import ContentBase, ryl_audit
from app.db.models.genre import Genre
from app.db.models.level import Level


@ryl_audit()
class LevelGenre(ContentBase):
    """Association between a Level and a Genre."""

    __tablename__ = "level_genres"

    level_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Level.id), nullable=False
    )
    genre_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Genre.id), nullable=False
    )

    # Relationships
    level = relationship("Level", back_populates="genres")
    genre = relationship("Genre", back_populates="level_genres")

    def __init__(self, level_id: int, genre_id: int):
        self.level_id = level_id
        self.genre_id = genre_id
