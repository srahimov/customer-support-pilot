from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class SupportResponse(BaseModel):
    """The final answer and classification of a support request."""

    category: Literal[
        "customer_account",
        "policy_service",
        "billing",
        "document_delivery",
        "technical_support",
        "claims",
        "quote",
        "general",
    ] = Field(
        description="The department best suited to handle the user's request."
    )

    customer_id: str | None = Field(
        description=(
            "The customer ID provided in the conversation, "
            "or null if no ID was provided."
        )
    )

    answer: str = Field(
        description=(
            "The customer-facing answer. Ground customer-specific facts "
            "in tool results, and ask for missing information when needed."
        )
    )


TicketStatus = Literal[
    "open",
    "in_progress",
    "waiting_for_customer",
    "resolved",
]


class TicketUpdateRequest(BaseModel):
    """A proposed update to an existing customer's support ticket."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    customer_id: str = Field(
        min_length=1,
        description="The customer who owns the ticket.",
    )

    ticket_id: str = Field(
        min_length=1,
        description="The exact ticket to update.",
    )

    expected_version: int = Field(
        ge=1,
        strict=True,
        description="The version returned by the latest ticket lookup.",
    )

    new_status: TicketStatus = Field(
        description="The proposed ticket status.",
    )

    note: str = Field(
        min_length=1,
        max_length=1000,
        description=(
            "The proposed latest_update text explaining the ticket status."
        ),
    )