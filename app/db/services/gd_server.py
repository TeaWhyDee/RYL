from typing import Optional

from app import db
from app.db.models.gd_server import GDServer
from app.db.models.level import GDVersion
from app.utility.context import ContextValues
from app.utility.exceptions import RYLAlreadyExists
from app.utility.util import sanitize_for_url


def get_gd_server(id: int):
    server = GDServer.query.filter_by(id=id).one_or_none()
    return server


def try_add_gd_server(
    ctx: ContextValues,
    name: str,
    ip: str,
    gd_version: GDVersion,
    description: Optional[str] = None,
):
    url_name = sanitize_for_url(name)

    server = GDServer.query.filter_by(url_name=url_name).one_or_none()
    if server:
        raise RYLAlreadyExists(
            f"GDServer with url_name {url_name} already exists"
        )

    new_server = GDServer(
        display_name=name,
        url_name=url_name,
        ip=ip,
        gd_version=gd_version,
        description=description,
    )

    ctx.set()
    db.session.add(new_server)
    db.session.commit()

    return new_server


def get_all_servers():
    return GDServer.query.order_by(GDServer.gd_version).all()
