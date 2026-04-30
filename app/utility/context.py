from typing import Optional

from sqlalchemy_declarative_extensions.audit import set_context_values

from app.db.database import db


class ContextValues:
    """
    Set context values for audit table entries.
    Values that can be set:
    - user_id
    - note

    Example:
    context_values = ContextValues(note="demonlist")
    context_values = ContextValues(user_id=self.user_id)
    """

    user_id: int
    note: Optional[str]

    def set(self):
        """
        Sets context for the next ONE transaction.
        i.e. until db.session.commit()
        """
        # if self.user_id:
        set_context_values(db.session, user_id=self.user_id)

        if self.note:
            set_context_values(db.session, note=self.note)

    def __init__(
        self,
        # user_id: Optional[int] = None,
        user_id: int,
        note: Optional[str] = None,
    ):
        self.user_id = user_id
        self.note = note
