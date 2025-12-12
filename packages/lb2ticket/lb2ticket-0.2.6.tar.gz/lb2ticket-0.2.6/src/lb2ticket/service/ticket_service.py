from lb2ticket.service.api_service import APIService
from lb2ticket.model.ticket import Ticket, CloseTicket
from lb2ticket.model.comment import Comment
from datetime import datetime


class TicketService(APIService):
    def __init__(self, application_config):
        super().__init__(application_config=application_config)
        self.base_url = "v1/ticket"

    def create(self, title: str, description: str, action: str) -> Ticket:
        ticket = Ticket(title=title, description=description, action=action)
        json = self.post(ticket.serialize())
        new_ticket = Ticket()
        new_ticket.load_json(json)
        return new_ticket

    def find_by_id(self, ticket_id: str) -> Ticket:
        json = self.get(f"/{ticket_id}")
        if json == None:
            return None
        ticket = Ticket()
        ticket.load_json(json)
        return ticket

    def close(self, ticket_id: str, resolution: str):
        ticket = CloseTicket(id=ticket_id, resolution=resolution)
        self.put(path=f"/{ticket_id}/close", obj=ticket.serialize())

    def add_description(self, ticket_id: str, description: str):
        ticket = Ticket(id=ticket_id, description=description)
        self.put(path=f"/{ticket_id}/description", obj=ticket.serialize())

    def add_comment(self, ticket_id: str, comment: str):
        comment_dto = Comment(id=ticket_id, comment=comment)
        self.put(path=f"/{ticket_id}/comment", obj=comment_dto.serialize())

    def find_by_execution(self, execution_type: str) -> Ticket:
        json = self.get(f"/by-action/{execution_type}")
        if json == None:
            return None
        ticket = Ticket()
        ticket.load_json(json)
        return ticket
    
    def create_full(self, json):
        self.post("/create-full", json)
