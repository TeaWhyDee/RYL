"""database.py"""

import enum
from typing import Callable, TypeVar

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Integer,
    MetaData,
    String,
    func,
    types,
)
from sqlalchemy.orm import (  # DeclarativeBase,; MappedAsDataclass,
    Mapped,
    declarative_base,
    mapped_column,
)
from sqlalchemy_declarative_extensions import declarative_database
from sqlalchemy_declarative_extensions.audit import (
    audit_model,
    default_primary_key,
)

_Base = declarative_base()

audit_md = MetaData(
    naming_convention={
        "fk": "audit_%(table_name)s_id",
        "pk": "%(table_name)s_pk",
    }
)


# https://sqlalchemy-declarative-extensions.readthedocs.io/en/stable/audit_tables.html
@declarative_database
class Base(_Base):
    __abstract__ = True

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
            # "audit_table": "%(table_name)s_audit",
            # "audit_function": "%(schema)s_%(table_name)s_audit",
            # "audit_trigger": "%(schema)s_%(table_name)s_audit",
        }
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class CompletenessStatus(enum.Enum):
    #
    bad = 0
    imported_GD = 1
    imported_GD_plus = 2
    imported_extra = 3
    imported_extra_plus = 4
    #
    user_edited = 5
    user_edited_plus = 6
    helper_edited = 7
    mod_edited = 8
    approved_awaiting_correction = 9
    mod_approved = 10


class ContentBase(Base):
    __abstract__ = True


ignore_columns = set(["created_at", "updated_at"])
context_columns = [
    # User id is set in utility/auth.py
    # User_id should be set to 1 for system operations. Note is optional extra info.
    Column("user_id", String(), nullable=True),
    Column("note", String(500), nullable=True),
    # TODO: datetime
]
T = TypeVar("T")


def ryl_audit(
    *,
    insert: bool = True,
    update: bool = True,
    delete: bool = True,
) -> Callable[[T], T]:
    def decorator(model: T) -> T:
        return audit_model(
            model,
            primary_key=default_primary_key,
            schema=None,
            ignore_columns=ignore_columns,
            context_columns=context_columns,
            insert=insert,
            update=update,
            delete=delete,
        )

    return decorator


db = SQLAlchemy(model_class=Base)
