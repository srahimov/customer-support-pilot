import json

from langgraph.types import Interrupt
from pydantic import ValidationError

from customer_support_pilot.context import SupportContext
from customer_support_pilot.schemas import TicketUpdateRequest


def review_ticket_update(
    pending: Interrupt,
    context: SupportContext,
) -> dict | None:
    action = pending.value

    if (
        action.get("type") != "tool_approval"
        or action.get("name") != "update_ticket"
    ):
        raise RuntimeError("Unsupported approval request.")

    try:
        proposal = TicketUpdateRequest.model_validate(
            action["args"].get("request")
        )
    except ValidationError:
        return {
            "type": "reject",
            "message": "Invalid ticket update. Ask for corrected information.",
        }

    if (
        context.role not in {"support_agent", "supervisor"}
        or proposal.customer_id.upper() not in context.allowed_customer_ids
    ):
        return {
            "type": "reject",
            "message": "Current employee permissions deny this update.",
        }

    edited = False

    while True:
        print("\nPending ticket update:")
        print(json.dumps(proposal.model_dump(), indent=2))

        try:
            choice = input(
                "Review [approve / edit / reject / later]: "
            ).strip().lower()

            if choice in {"later", "exit", "/exit"}:
                return None

            if choice == "reject":
                return {
                    "type": "reject",
                    "message": (
                        "The reviewer rejected this update. Do not retry "
                        "unless the employee explicitly requests it again."
                    ),
                }

            if choice == "edit":
                status = input(
                    f"Status [{proposal.new_status}]: "
                ).strip()
                note = input(
                    "New note [Enter keeps the current proposal]: "
                ).strip()

                values = proposal.model_dump()
                values["new_status"] = status or proposal.new_status
                values["note"] = note or proposal.note

                try:
                    proposal = TicketUpdateRequest.model_validate(values)
                except ValidationError as error:
                    print(error)
                    continue

                edited = True
                continue

            if choice == "approve":
                if edited:
                    return {
                        "type": "edit",
                        "edited_action": {
                            "name": "update_ticket",
                            "args": {"request": proposal.model_dump()},
                        },
                    }

                return {"type": "approve"}

            print("Enter approve, edit, reject, or later.")

        except (EOFError, KeyboardInterrupt):
            print()
            return None