from typing import Optional

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import ContentBase, ryl_audit
from app.db.models.gd_account import GDAccount
from app.db.models.gd_server import GDServer
from app.db.models.level import GDVersion, Level, LevelDifficulty, LevelRating


@ryl_audit()
class LevelUpload(ContentBase):
    """
    An upload of a level to a GD server - has GD ID, creator, etc.
    """

    __tablename__ = "level_uploads"

    gdid: Mapped[int] = mapped_column(Integer, nullable=False)
    gd_title: Mapped[str] = mapped_column(String, nullable=False)

    gd_rating: Mapped[LevelRating] = mapped_column(
        Enum(LevelRating), nullable=False
    )
    gd_difficulty: Mapped[LevelDifficulty] = mapped_column(
        Enum(LevelDifficulty), nullable=False
    )
    gd_version_original: Mapped[GDVersion | None] = mapped_column(
        Enum(GDVersion), nullable=True
    )
    gd_version_last: Mapped[GDVersion | None] = mapped_column(
        Enum(GDVersion), nullable=True
    )
    song_ngid: Mapped[int] = mapped_column(Integer, nullable=False)
    gd_cache_likes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    note: Mapped[str | None] = mapped_column(String, nullable=True)

    # Foreign
    gd_account_id: Mapped[int] = mapped_column(
        "gd_account_id", ForeignKey(GDAccount.id)
    )
    level_id: Mapped[int] = mapped_column(ForeignKey(Level.id))
    gd_server_id: Mapped[int] = mapped_column(ForeignKey(GDServer.id))

    # relationships
    gd_server = relationship("GDServer", back_populates="level_uploads")
    level = relationship("Level", back_populates="uploads")
    gd_account = relationship("GDAccount", back_populates="level_uploads")

    def __init__(
        self,
        gdid: int,
        gd_title: str,
        gd_server_id: int,
        song_ng_id: int,
        gd_account_id: int,
        gd_rating: LevelRating,
        gd_difficulty: LevelDifficulty,
        level_id: int,
        note: Optional[str],
        gd_cache_likes: Optional[int],
        gd_version_original: Optional[GDVersion],
        gd_version_last: Optional[GDVersion],
    ):
        self.gdid = gdid
        self.gd_title = gd_title
        self.gd_server_id = gd_server_id

        self.gd_rating = gd_rating
        self.gd_difficulty = gd_difficulty
        self.song_ngid = song_ng_id
        self.gd_account_id = gd_account_id
        self.level_id = level_id
        self.gd_cache_likes = gd_cache_likes
        self.gd_version_original = gd_version_original
        self.gd_version_last = gd_version_last

        self.note = note
