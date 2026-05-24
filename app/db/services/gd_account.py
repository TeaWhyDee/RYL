from typing import Optional

from app import db
from app.db.database import CompletenessStatus
from app.db.models.gd_account import GDAccount
from app.db.models.gd_server import GDServer
from app.db.models.team import Team
from app.utility.context import ContextValues
from app.utility.exceptions import RYLAlreadyExists
from app.utility.util import sanitize_for_url


def get_gd_account(id: int):
    account = GDAccount.query.filter_by(id=id).one_or_none()
    return account


def find_gd_account(gdid: int):
    account = GDAccount.query.filter_by(gd_account_gdid=gdid).one_or_none()
    return account


def try_add_gd_account(
    ctx: ContextValues,
    username: str,
    gd_account_gdid: int,
    gd_server_id: int,
):
    server = GDServer.query.filter_by(id=gd_server_id).first()
    if not server:
        raise ValueError(f"GD Server id {gd_server_id} does not exist")

    existing = (
        GDAccount.query.filter(GDAccount.gd_account_gdid == gd_account_gdid)
        .filter(GDAccount.gd_server_id == gd_server_id)
        .one_or_none()
    )

    if existing:
        raise RYLAlreadyExists(
            f"GDAccount with gdid {gd_account_gdid} on server {gd_server_id} already exists: id {existing.id}"
        )

    new_account = GDAccount(
        username=username,
        gd_account_gdid=gd_account_gdid,
        gd_server_id=gd_server_id,
    )

    ctx.set()
    db.session.add(new_account)
    db.session.commit()

    return new_account
