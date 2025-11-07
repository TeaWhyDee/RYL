from typing import Optional

from sqlalchemy_declarative_extensions.audit import set_context_values

from app.db.database import db


class ContextValues:
    user_id: Optional[int]
    note: Optional[str]

    def set(self):
        if self.user_id:
            set_context_values(db.session, user_id=self.user_id)
        if self.note:
            set_context_values(db.session, user_id=self.note)

    def __init__(
        self,
        user_id: Optional[int] = None,
        note: Optional[str] = None,
    ):
        self.user_id = user_id
        self.note = note
