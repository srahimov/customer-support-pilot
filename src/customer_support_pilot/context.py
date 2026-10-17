from dataclasses import dataclass
from typing import Literal

from customer_support_pilot.repositories import TicketRepository


@dataclass(frozen=True)
class SupportContext:
    employee_id: str
    role: Literal["support_agent", "supervisor", "guest"]
    allowed_customer_ids: frozenset[str]
    ticket_repository: TicketRepository