from typing import TYPE_CHECKING, List

from models.pill import Pill


class User(object):
    if TYPE_CHECKING:
        from .pill import Pill

        name: str
        pills: List[Pill]
        
        
    def __init__(self, *, state, data):
        self._state = state 

        self._from_data(data)
    
    def _from_data(self, user: dict):
        self.name = user['name']
        self._id = user['id']
        self.count =  user["count"]
        self.flair = user["flair"]
        
        self.pills = [Pill(state=self._state, data=pill) for pill in user['pills']]
        
    def __repr__(self):
        return f"User(name='{self.name}', id='{self._id}')"