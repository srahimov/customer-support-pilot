from langchain.tools import tool, ToolRuntime
from customer_support_pilot.records import CUSTOMERS, POLICIES, INVOICES
from customer_support_pilot.context import SupportContext
from langchain.messages import ToolMessage
from langgraph.types import Command
from customer_support_pilot.schemas import TicketUpdateRequest

from customer_support_pilot.state import Department, SupportState

@tool
def lookup_customer(customer_id: str, runtime: ToolRuntime[SupportContext],) -> dict:

    """
    Retrieve a customer profile using an exact customer ID.
    The profile does not establish insurance coverage.
    """

    normalized_id = customer_id.strip().upper()
    context = runtime.context

    if (
        context is None
        or context.role not in {"support_agent", "supervisor"}
        or normalized_id not in context.allowed_customer_ids
    ):
        return {
            "status": "forbidden",
            "customer_id": normalized_id,
            "customer": None,
        }

    customer = CUSTOMERS.get(normalized_id)

    return {
        "status": "found" if customer is not None else "not_found",
        "customer_id": normalized_id,
        "customer": customer,
    }

@tool
def lookup_policies(customer_id: str,runtime: ToolRuntime[SupportContext],) -> dict:
    """Retrieve insurance policy records belonging to a customer.

    Use for policy numbers, products, recorded statuses, and policy dates.
    These records do not determine coverage for a particular loss.
    """
    normalized_id = customer_id.strip().upper()
    context = runtime.context

    if (
        context is None
        or context.role not in {"support_agent", "supervisor"}
        or normalized_id not in context.allowed_customer_ids
    ):
        return {
            "status": "forbidden",
            "customer_id": normalized_id,
            "policies": [],
        }

    if normalized_id not in CUSTOMERS:
        return {
            "status": "customer_not_found",
            "customer_id": normalized_id,
            "policies": [],
        }

    policies = [
        policy
        for policy in POLICIES.values()
        if policy["customer_id"] == normalized_id
    ]

    return {
        "status": "found" if policies else "no_policies",
        "customer_id": normalized_id,
        "policies": policies,
    }


@tool
def lookup_billing(customer_id: str,runtime: ToolRuntime[SupportContext],) -> dict:
    """Retrieve a customer's invoices, recorded paid amounts, and balances in USD.

    This tool reads billing records; it cannot collect payments or issue refunds.
    """
    normalized_id = customer_id.strip().upper()
    context = runtime.context

    if (
        context is None
        or context.role not in {"support_agent", "supervisor"}
        or normalized_id not in context.allowed_customer_ids
    ):
        return {
            "status": "forbidden",
            "customer_id": normalized_id,
            "invoices": [],
        }

    if normalized_id not in CUSTOMERS:
        return {
            "status": "customer_not_found",
            "customer_id": normalized_id,
            "invoices": [],
        }

    invoices = []

    for invoice in INVOICES.values():
        if invoice["customer_id"] == normalized_id:
            balance = invoice["amount_cents"] - invoice["paid_cents"]

            invoices.append({
                **invoice,
                "balance_cents": balance,
                "balance_display": (
                    f"${balance // 100:,}.{balance % 100:02d}"
                ),
            })

    return {
        "status": "found" if invoices else "no_invoices",
        "customer_id": normalized_id,
        "invoices": invoices,
    }

@tool
def lookup_tickets(
    customer_id: str,
    runtime: ToolRuntime[SupportContext],
    ticket_id: str | None = None,
) -> dict:
    """Retrieve a customer's support tickets or one exact ticket belonging to them.

    Use for the current ticket status, assigned department, subject, and update.
    This tool does not create, update, or close tickets.
    """
    normalized_id = customer_id.strip().upper()
    normalized_ticket_id = ticket_id.strip().upper() if ticket_id else None
    context = runtime.context

    if (
        context is None
        or context.role not in {"support_agent", "supervisor"}
        or normalized_id not in context.allowed_customer_ids
    ):
        return {
            "status": "forbidden",
            "customer_id": normalized_id,
            "tickets": [],
        }

    if normalized_id not in CUSTOMERS:
        return {
            "status": "customer_not_found",
            "customer_id": normalized_id,
            "tickets": [],
        }

    tickets = context.ticket_repository.find_for_customer(
        customer_id=normalized_id,
        ticket_id=normalized_ticket_id,
    )

    return {
        "status": "found" if tickets else "no_matching_tickets",
        "customer_id": normalized_id,
        "tickets": tickets,
    }

@tool
def handoff_to_department(
    department: Department,
    runtime: ToolRuntime[SupportContext, SupportState],
) -> Command:
    """Switch the conversation to the department suited to the current task.

    Departments: customer_account for profiles; billing for invoices and payments;
    document_delivery for document requests; technical_support for portal issues;
    policy_service for policy questions; triage for unclear or general requests.
    Call this tool alone, without any other tool calls in the same response.
    """
    return Command(
        update={
            "active_department": department,
            "messages": [
                ToolMessage(
                    content=f"Active department changed to {department}.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool
def update_ticket(
    request: TicketUpdateRequest,
    runtime: ToolRuntime[SupportContext],
) -> dict:
    """Update an existing ticket's status and latest update after human review.

    First retrieve the exact ticket with lookup_tickets and use its version.
    This updates support-ticket records, not insurance coverage or payments.
    Call this tool alone. Human approval is required before it executes.
    """
    customer_id = request.customer_id.strip().upper()
    context = runtime.context

    if (
        context is None
        or context.role not in {"support_agent", "supervisor"}
        or customer_id not in context.allowed_customer_ids
    ):
        return {"status": "forbidden", "customer_id": customer_id}

    try:
        ticket = context.ticket_repository.update_if_version_matches(
            request
        )
    except ConnectionError:
        return {
            "status": "unknown_outcome",
            "message": (
                "The update could not be confirmed. It may have committed. "
                "Do not automatically retry; verify the ticket first."
            ),
        }

    if ticket is None:
        return {
            "status": "conflict_or_not_found",
            "message": (
                "No update was applied because the customer, ticket, or "
                "version did not match. Retrieve the ticket again and "
                "obtain fresh approval before any new update."
            ),
        }

    return {
        "status": "updated",
        "customer_id": customer_id,
        "ticket": ticket,
    }