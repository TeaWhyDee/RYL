"""
Simply a GD user account to tag the uploader of a level
Needed in case a user account changes username.
Also can link to the user in GDBrowser.
"""

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_declarative_extensions.audit import audit

from app.db.database import ContentBase, ryl_audit


@ryl_audit()
class GDAccount(ContentBase):
    """
    Must have a creator attached to attach new level uploads.
    """

    __tablename__ = "gd_account"

    username: Mapped[str] = mapped_column(String(50), unique=True)
    GD_id: Mapped[int] = mapped_column(Integer)

    # TODO
    # GDPS = Mapped[str] = mapped_column(String(50))
    # add constraint

    # = relationships =
    # levels = relationship("Level", back_populates="GD_publisher")
    level_uploads = relationship("LevelUpload", back_populates="GD_account")

    def __init__(self, username: str):
        self.username = username
