
from typing import TYPE_CHECKING, Optional


class Pill(object):
    if TYPE_CHECKING:
        from .user import User

        name: str
        comment_id: Optional[str]
        from_user: Optional[str] #TODO: make userRef object
        date: Optional[int] # TODO: impl better date parsing 
        amount: int
        owner: User

    def __init__(self, *, state, user: "User", data: dict):
        self._state = state 

        self.owner = user
        
        self._from_data(data)
    
    def __repr__(self):
        return f"Pill(name='{self.name}', comment_id='{self.comment_id}')"

    def _from_data(self, pill: dict):
        self.name = pill['name']
        self.comment_id = pill.get("commentID")
        self.from_user = pill.get("fromUser")
        
        if date := pill.get("date"):
            self.date = int(date)
        else:
            self.date = None

        self.amount = pill.get('amount', 1)