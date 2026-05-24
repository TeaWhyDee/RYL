from typing import List

from app.db.models.user import UserRole

"""
This file provides a CRUD_AUTH_ROLES constant that can be applied to a route like:
```
@app_team.auth_required(ryl_auth, roles=CRUD_AUTH_ROLES["team"].delete)
```

A typical 'roles' parameter looks like: ["helper", "moderator", "admin"],
i.e listing every role that can access an endpoint.

For this purpose, we map each role to a list of itself and all higher roles
when constructing the var.
"""


_role_mapping = {
    UserRole.normal.name: [
        UserRole.normal.name,
        UserRole.helper.name,
        UserRole.moderator.name,
        UserRole.admin.name,
    ],
    UserRole.helper.name: [
        UserRole.helper.name,
        UserRole.moderator.name,
        UserRole.admin.name,
    ],
    UserRole.moderator.name: [
        UserRole.moderator.name,
        UserRole.admin.name,
    ],
    UserRole.admin.name: [
        UserRole.admin.name,
    ],
}


class CRUDAuthRoles:
    # read: UserRole = UserRole.normal
    # create: UserRole = UserRole.normal
    # update: UserRole = UserRole.normal
    # delete: UserRole = UserRole.normal
    read: List[str] = [UserRole.normal.name]
    create: List[str] = [UserRole.normal.name]
    update: List[str] = [UserRole.normal.name]
    delete: List[str] = [UserRole.normal.name]

    def __init__(self, read, create, update, delete) -> None:
        self.read = _role_mapping[read.name]
        self.create = _role_mapping[create.name]
        self.update = _role_mapping[update.name]
        self.delete = _role_mapping[delete.name]


#
# Consts
#
CRUD_AUTH_ROLES = {
    "creator": CRUDAuthRoles(
        read=UserRole.normal,
        create=UserRole.normal,
        update=UserRole.helper,
        delete=UserRole.admin,
    ),
    "team": CRUDAuthRoles(
        read=UserRole.normal,
        create=UserRole.normal,
        update=UserRole.normal,
        delete=UserRole.normal,
    ),
    "team_member": CRUDAuthRoles(
        read=UserRole.normal,
        create=UserRole.normal,
        update=UserRole.helper,
        delete=UserRole.helper,
    ),
    "level": CRUDAuthRoles(
        read=UserRole.normal,
        create=UserRole.normal,
        update=UserRole.normal,
        delete=UserRole.admin,
    ),
    "level_upload": CRUDAuthRoles(
        read=UserRole.normal,
        create=UserRole.moderator,
        update=UserRole.moderator,
        delete=UserRole.moderator,
    ),
    "level_credit": CRUDAuthRoles(
        read=UserRole.normal,
        create=UserRole.normal,
        update=UserRole.helper,
        delete=UserRole.moderator,
    ),
    "level_authorship": CRUDAuthRoles(
        read=UserRole.normal,
        create=UserRole.normal,
        update=UserRole.helper,
        delete=UserRole.moderator,
    ),
    "gd_account": CRUDAuthRoles(
        read=UserRole.normal,
        create=UserRole.moderator,
        update=UserRole.moderator,
        delete=UserRole.moderator,
    ),
    "gd_server": CRUDAuthRoles(
        read=UserRole.normal,
        create=UserRole.moderator,
        update=UserRole.moderator,
        delete=UserRole.moderator,
    ),
    "genre": CRUDAuthRoles(
        read=UserRole.normal,
        create=UserRole.moderator,
        update=UserRole.moderator,
        delete=UserRole.admin,
    ),
    "level_genre": CRUDAuthRoles(
        read=UserRole.normal,
        create=UserRole.moderator,
        update=UserRole.moderator,
        delete=UserRole.moderator,
    ),
}
