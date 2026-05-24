"""
Simply a GD user account to tag the uploader of a level
Needed in case a user account changes username.
Also can link to the user in GDBrowser.
"""

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_declarative_extensions.audit import audit

from app.db.database import ContentBase, ryl_audit
from app.db.models.gd_server import GDServer


@ryl_audit()
class GDAccount(ContentBase):
    """
    Must have a creator attached to attach new level uploads.
    """

    __tablename__ = "gd_account"

    username: Mapped[str] = mapped_column(String(50), unique=False)
    gd_account_gdid: Mapped[int] = mapped_column(Integer, nullable=False)

    gd_server_id: Mapped[int] = mapped_column(
        ForeignKey(GDServer.id), nullable=False
    )

    # = relationships =
    level_uploads = relationship("LevelUpload", back_populates="gd_account")
    gd_server = relationship("GDServer", back_populates="gd_accounts")

    def __init__(self, username: str, gd_account_gdid: int, gd_server_id: int):
        self.username = username
        self.gd_account_gdid = gd_account_gdid
        self.gd_server_id = gd_server_id

    # TODO
    # constraints - unique combo of gd_accountgdid + gd_server
