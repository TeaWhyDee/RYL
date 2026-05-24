"""
GD Server with IP and name.
Examples: 1.9 GDPS; Main RobTop server.
"""

import enum
from typing import Optional

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Sequence, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_declarative_extensions.audit import audit

from app.db.database import ContentBase, ryl_audit
from app.db.models.level import GDVersion


@ryl_audit()
class GDServer(ContentBase):
    __tablename__ = "gd_server"

    url_name: Mapped[str] = mapped_column(String(60), nullable=False)
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    # icon

    gd_version: Mapped[GDVersion] = mapped_column(
        Enum(GDVersion), nullable=False
    )

    IP: Mapped[str] = mapped_column(String, nullable=False)

    # = relationships =
    level_uploads = relationship("LevelUpload", back_populates="gd_server")
    gd_accounts = relationship("GDAccount", back_populates="gd_server")

    def __init__(
        self,
        display_name: str,
        url_name: str,
        ip: str,
        gd_version: GDVersion,
        description: Optional[str] = None,
    ):
        self.display_name = display_name
        self.url_name = url_name
        self.IP = ip
        self.gd_version = gd_version
        self.description = description
