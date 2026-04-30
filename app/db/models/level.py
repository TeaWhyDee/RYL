import enum
from datetime import date
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Date,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base, CompletenessStatus, ContentBase, db, ryl_audit
from app.db.models.song import Song
from app.utility.util import sanitize_for_url


class LevelLength(enum.Enum):
    tiny = "tiny"
    short = "short"
    medium = "medium"
    long = "L"
    XL = "XL"  # 2+ minutes
    XXL = "XXL"  # 5+ minutes  (travel)
    XXXL = "absurd"  # 15+ minutes


class LevelType(enum.Enum):
    level = "level"
    layout = "layout"
    challenge = "challenge"
    minigame = "minigame"
    platformer = "platformer"


class LevelRating(enum.Enum):
    unrated = "unrated"
    rated = "rated"
    featured = "featured"
    epic = "epic"
    legendary = "legendary"
    mythic = "mythic"


class LevelDifficulty(enum.Enum):
    na = "na"
    auto = "auto"
    easy = "easy"
    normal = "normal"
    hard = "hard"
    harder = "harder"
    insane = "insane"

    demon = "demon"  # unspecified demon
    easy_demon = "easy demon"
    medium_demon = "medium demon"
    hard_demon = "hard demon"
    insane_demon = "insane demon"
    extreme_demon = "extreme demon"


class GDVersion(enum.Enum):
    ver10 = 100
    ver11 = 110  # mirror
    ver12 = 120  # ball
    ver13 = 130  #
    ver14 = 140  # mini
    ver15 = 150  # ufo
    ver16 = 160  # clubstep
    ver17 = 170  # speed
    ver18 = 180  # dual
    ver19 = 190  # wave
    ver20 = 200
    ver21 = 210
    ver22 = 220
    # ver221 = 221


#
# @ryl_audit()
# class GD_LevelInfo(ContentBase):
#     __tablename__ = "GD_levelinfo"


@ryl_audit()
class Level(ContentBase):
    __tablename__ = "levels"

    # == Main Info ==
    GD_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, unique=True
    )
    url_name: Mapped[str] = mapped_column(String(50), nullable=False)
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)
    level_type: Mapped[LevelType | None] = mapped_column(
        Enum(LevelType), nullable=False
    )

    # nullable
    date_showcased: Mapped[Date | None] = mapped_column(Date, nullable=True)
    date_published: Mapped[Date | None] = mapped_column(Date, nullable=True)
    length: Mapped[LevelLength | None] = mapped_column(
        Enum(LevelLength), nullable=True
    )
    length_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    GD_rating: Mapped[LevelRating | None] = mapped_column(
        Enum(LevelRating), nullable=True
    )
    GD_difficulty: Mapped[LevelDifficulty | None] = mapped_column(
        Enum(LevelDifficulty), nullable=True  # null = no GD difficulty
    )
    GD_version: Mapped[GDVersion] = mapped_column(
        Enum(GDVersion), nullable=True
    )

    # == website info ==
    average_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_megacollab: Mapped[bool] = mapped_column(Boolean)
    is_upcoming: Mapped[bool] = mapped_column(Boolean)

    completeness_status: Mapped[CompletenessStatus] = mapped_column(
        Enum(
            CompletenessStatus,
            nullable=False,
        ),
        default=CompletenessStatus.imported_GD,
    )

    # == Relaionships ==
    # GD_publisher_id: Mapped[int] = mapped_column(
    #     "gd_publisher_id", ForeignKey(GD_account.id), nullable=True
    # )  # null = not published

    song_id: Mapped[Song] = mapped_column(
        "song_id", ForeignKey(Song.id), nullable=True
    )

    credits = relationship("LevelCredit", back_populates="level")
    level_uploads = relationship("LevelUpload", back_populates="level")
    song = relationship("Song", back_populates="levels")

    @hybrid_property
    def url(self) -> str:
        return f"/level/{self.url_name}"

    def __init__(
        self,
        GD_id: int,
        name: str,
        completeness_status: CompletenessStatus,
        level_type: Optional[LevelType] = None,
        level_length: Optional[LevelLength] = None,
        level_length_seconds: Optional[int] = None,
        level_rating: Optional[LevelRating] = None,
        date_showcased: Optional[Date] = None,
        date_published: Optional[Date] = None,
    ):
        self.completeness_status = completeness_status

        self.GD_id = GD_id
        self.url_name = sanitize_for_url(name)
        self.display_name = name

        self.level_type = level_type
        self.date_showcased = date_showcased
        self.date_published = date_published
        self.length = level_length
        self.length_seconds = level_length_seconds

        self.GD_rating = level_rating
        self.GD_difficulty = None
        self.GD_version = GDVersion.ver22
        self.average_rating = None
        # self.GD_publisher_id = GD_publisher_id
        # self.creator_id = creator_id

        self.is_upcoming = False
        self.is_megacollab = False
