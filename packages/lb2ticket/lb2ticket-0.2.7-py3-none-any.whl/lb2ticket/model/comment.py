
from lb2ticket.model.base_model import BaseModel
from dataclasses import dataclass

@dataclass
class Comment(BaseModel):
    id = None
    comment = None
    action_time = None

    def __init__(self, comment=None, id=None, action_time=None):
        self.comment = comment
        self.id=id
        self.action_time = action_time

    # @property
    def serialize(self):
        return {
           'id': self.id,
           'comment': self.comment
        }