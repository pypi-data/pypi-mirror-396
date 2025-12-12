from lb2ticket.model.base_model import BaseModel
from dataclasses import dataclass

@dataclass
class Task(BaseModel):
    id = None
    title = None
    number = None
    ticketId = None

    def __init__(self, title=None, ticket_id=None):
        self.title = title
        self.ticketId=ticket_id

    # @property
    def serialize(self):
        return {
           'id': self.id,
           'title': self.title,
           'number': self.number,
           'ticketId': self.ticketId
        }
    
@dataclass
class CloseTask(BaseModel):
    id = None
    comment = None

    def __init__(self, comment=None, id=None):
        self.comment = comment
        self.id=id
    
    # @property
    def serialize(self):
        return {
           'id': self.id,
           'comment': self.comment
        }