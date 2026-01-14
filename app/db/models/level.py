import enum
from datetime import date
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import ContentBase, ryl_audit
from app.utility.util import sanitize_url


class GDLength(enum.Enum):
    tiny = "tiny"
    short = "short"
    medium = "medium"
    long = "L"
    XL = "XL"
    XXL = "XXL"  # > 5 minutes


class LevelType(enum.Enum):
    level = "level"
    platformer = "platformer"
    layout = "layout"
    challenge = "challenge"
    minigame = "minigame"


class GDRating(enum.Enum):
    unrated = "unrated"
    rated = "rated"
    featured = "featured"
    epic = "epic"
    legendary = "legendary"
    mythic = "mythic"


class GDDifficulty(enum.Enum):
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
    ver10 = 100  # 1.0
    ver11 = 110  # mirror
    ver12 = 120  # ball
    ver13 = 130  #
    ver14 = 140  # mini
    ver15 = 150  # ufo
    ver16 = 160  # clubstep
    ver17 = 170  # 3x speed
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
    GD_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, unique=True
    )
    url_name: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True
    )
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)

    date_published: Mapped[date] = mapped_column(DateTime, nullable=True)
    GD_publisher: Mapped[str | None] = mapped_column(
        String(50), nullable=True  # null = not published
    )
    GD_difficulty: Mapped[GDDifficulty | None] = mapped_column(
        Enum(GDDifficulty), nullable=True  # null = no GD difficulty
    )
    GD_version: Mapped[GDVersion | None] = mapped_column(
        Enum(GDVersion), nullable=True  # null = unknown; unset
    )

    GD_length: Mapped[GDLength | None] = mapped_column(Enum(GDLength))
    GD_rating: Mapped[GDRating | None] = mapped_column(Enum(GDRating))

    # == website info ==
    level_type: Mapped[LevelType] = mapped_column(
        Enum(LevelType), nullable=False
    )
    is_megacollab: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    is_upcoming: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # == derived / cached ==
    # average_rating: Mapped[int] = mapped_column(Integer, nullable=True)

    @hybrid_property
    def url(self) -> str:
        return f"/level/{self.url_name}"

    # == Relaionships ==
    author_creators = relationship("LevelAuthorCreator", back_populates="level")
    author_teams = relationship("LevelAuthorTeam", back_populates="level")
    credits = relationship("LevelCredit", back_populates="level")

    def __init__(
        self,
        GD_id: Optional[int],
        name: str,
        GD_publisher: str,
        level_length: Optional[GDLength],
        level_rating: Optional[GDRating],
        level_type: LevelType = LevelType.level,
    ):
        self.GD_id = GD_id
        self.display_name = name
        self.url_name = sanitize_url(name)
        self.GD_publisher = GD_publisher
        # self.creator_id = creator_id
        self.level_type = level_type
        self.GD_length = level_length
        self.GD_rating = level_rating

        self.is_upcoming = False
        self.is_megacollab = False
