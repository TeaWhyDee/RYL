# UNUSED


import typing as t

from apiflask.blueprint import APIBlueprint
from apiflask.scaffold import _annotate, _ensure_sync
from apiflask.types import DecoratedType, HTTPAuthType
from sqlalchemy_declarative_extensions.audit import set_context_values


class RYL_APIBlueprint(APIBlueprint):

    def ryl_auth_required(
        self,
        auth: HTTPAuthType,
        roles: list | None = None,
        optional: str | None = None,
    ) -> t.Callable[[DecoratedType], DecoratedType]:

        def decorator(f):
            f = _ensure_sync(f)
            _annotate(f, auth=auth, roles=roles or [])
            return auth.login_required(role=roles, optional=optional)(f)

        return decorator


# UNUSED
