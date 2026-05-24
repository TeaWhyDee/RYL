from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import ContentBase, db, ryl_audit


@ryl_audit()
class Song(ContentBase):
    __tablename__ = "songs"

    ngid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    artist: Mapped[str] = mapped_column(String, nullable=False)

    is_nong: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_replacement: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # == Relaionships ==
    levels = relationship("Level", back_populates="song")

    def __init__(self, title: str, artist: str):
        self.ngid = None
        self.title = title
        self.artist = artist

        self.is_nong = False
        self.has_replacement = False

    # def init_NG(self, NG_ID: int):
    #     self.NG_ID = NG_ID
    # self.title = title
    # self.artist = artist

    # self.is_nong = False
    # self.has_replacement = False
