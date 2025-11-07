import enum
from datetime import date
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base, ContentBase, db, ryl_audit
from app.db.models.creator import Creator, Team
from app.utility.util import sanitize_url


class LevelLength(enum.Enum):
    tiny = "tiny"
    short = "short"
    medium = "medium"
    long = "L"
    XL = "XL"
    XXL = "XXL"


class LevelType(enum.Enum):
    level = "level"
    layout = "layout"
    challenge = "challenge"
    minigame = "minigame"


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


@ryl_audit()
class Level(ContentBase):
    __tablename__ = "levels"

    # == In-game Info ==
    GD_id: Mapped[int] = mapped_column(Integer, nullable=True, unique=True)
    url_name: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # USED IN URL
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)

    date_published: Mapped[date] = mapped_column(DateTime, nullable=True)
    GD_publisher: Mapped[str] = mapped_column(
        String, nullable=True
    )  # null = not published
    GD_difficulty: Mapped[LevelDifficulty] = mapped_column(
        Enum(LevelDifficulty), nullable=True  # null = no GD difficulty
    )
    GD_version: Mapped[GDVersion] = mapped_column(
        Enum(GDVersion), nullable=True
    )

    # == website info ==
    average_rating: Mapped[int] = mapped_column(Integer, nullable=True)

    level_type: Mapped[LevelType | None] = mapped_column(Enum(LevelType))
    length: Mapped[LevelLength | None] = mapped_column(Enum(LevelLength))
    rating: Mapped[LevelRating | None] = mapped_column(Enum(LevelRating))

    is_megacollab: Mapped[bool] = mapped_column(Boolean)
    is_upcoming: Mapped[bool] = mapped_column(Boolean)

    # == Relaionships ==
    # creator_id: Mapped[int] = mapped_column("creator_id", ForeignKey(Creator.id))
    # team_id: Mapped[int] = mapped_column("team_id", ForeignKey(Team.id), nullable=True)
    # creator = relationship("Creator", back_populates="levels")
    credits = relationship("LevelCredit", back_populates="level")

    from sqlalchemy.ext.hybrid import hybrid_property

    @hybrid_property
    def url(self) -> str:
        return f"/level/{self.url_name}"

    def __init__(
        self,
        GD_id: int,
        name: str,
        GD_publisher: str,
        level_type: Optional[LevelType],
        level_length: Optional[LevelLength],
        level_rating: Optional[LevelRating],
    ):
        self.GD_id = GD_id
        self.display_name = name
        self.url_name = sanitize_url(name)
        self.GD_publisher = GD_publisher
        # self.creator_id = creator_id
        self.level_type = level_type
        self.length = level_length
        self.rating = level_rating

        self.is_upcoming = False
        self.is_megacollab = False
