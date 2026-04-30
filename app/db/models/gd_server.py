"""
GD Server with IP and name.
Examples: 1.9 GDPS; Main RobTop server.
"""

import enum
from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_declarative_extensions.audit import audit

from app.db.database import ContentBase, ryl_audit
from app.db.models.level import GDVersion


@ryl_audit()
class GDServer(ContentBase):
    __tablename__ = "gd_server"

    url_name: Mapped[str] = mapped_column(String, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    # icon

    GD_version: Mapped[GDVersion] = mapped_column(
        Enum(GDVersion), nullable=False
    )

    IP: Mapped[str] = mapped_column(String, nullable=False)

    # = relationships =
    level_uploads = relationship("LevelUpload", back_populates="GD_server")

    def __init__(self, username: str):
        self.username = username
