from typing import Literal, NotRequired

from langchain.agents import AgentState


Department = Literal[
    "triage",
    "customer_account",
    "billing",
    "document_delivery",
    "technical_support",
    "policy_service",
]


class SupportState(AgentState):
    active_department: NotRequired[Department]