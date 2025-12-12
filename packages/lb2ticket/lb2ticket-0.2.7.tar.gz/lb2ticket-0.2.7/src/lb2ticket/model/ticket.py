
from lb2ticket.model.base_model import BaseModel
from dataclasses import dataclass

@dataclass
class Ticket(BaseModel):
    id = None
    title = None
    description = None
    number = None
    clientId = None
    clientName = None
    action = None

    def __init__(self, title=None, description=None, action=None):
        self.description = description
        self.title=title
        self.action = action

    # @property
    def serialize(self):
        return {
           'id': self.id,
           'title': self.title,
           'description': self.description,
           'number': self.number,
           'clientId': self.clientId,
           'clientName': self.clientName,
           'action': self.action
        }
	
@dataclass
class CloseTicket(BaseModel):
    id = None
    resolution = None

    def __init__(self, id=None, resolution=None):
        self.id = id
        self.resolution=resolution

    # @property
    def serialize(self):
        return {
           'id': self.id,
           'resolution': self.resolution
        }