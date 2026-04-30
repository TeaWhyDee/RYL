from typing import Optional
from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import ContentBase, ryl_audit
from app.db.models.gd_account import GDAccount
from app.db.models.gd_server import GDServer
from app.db.models.level import Level, LevelDifficulty, LevelRating


@ryl_audit()
class LevelUpload(ContentBase):
    # An upload of a level to a GD server - has GD ID, creator, etc.
    __tablename__ = "level_uploads"

    GD_ID: Mapped[int] = mapped_column(Integer, nullable=False)
    GD_title: Mapped[str] = mapped_column(String, nullable=False)

    GD_rating: Mapped[LevelRating] = mapped_column(
        Enum(LevelRating), nullable=False
    )
    GD_difficulty: Mapped[LevelDifficulty] = mapped_column(
        Enum(LevelDifficulty), nullable=False
    )
    song_NG_ID: Mapped[int] = mapped_column(Integer, nullable=False)

    note: Mapped[str | None] = mapped_column(String, nullable=True)

    # Foreign
    GD_Account_id: Mapped[int] = mapped_column(
        "GD_Account_id", ForeignKey(GDAccount.id)
    )
    level_id: Mapped[int] = mapped_column(ForeignKey(Level.id))
    GD_server_id: Mapped[int] = mapped_column(ForeignKey(GDServer.id))

    # relationships
    GD_server = relationship("GDServer", back_populates="level_uploads")
    level = relationship("Level", back_populates="level_uploads")
    GD_account = relationship("GDAccount", back_populates="level_uploads")

    def __init__(
        self,
        gd_id: int,
        gd_title: str,
        song_ng_id: int,
        gd_account_id: int,
        gd_rating: LevelRating,
        gd_difficulty: LevelDifficulty,
        level_fk: int,
        note: Optional[str],
    ):
        self.GD_ID = gd_id
        self.GD_title = gd_title

        self.GD_rating = gd_rating
        self.GD_difficulty = gd_difficulty
        self.song_NG_ID = song_ng_id
        self.GD_Account_id = gd_account_id
        self.level_id = level_fk

        self.note = note
