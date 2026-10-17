from argparse import ArgumentParser
from uuid import UUID, uuid4

from dotenv import load_dotenv
from langchain.agents.middleware.model_call_limit import (
    ModelCallLimitExceededError,
)
from langchain.agents.middleware.tool_call_limit import (
    ToolCallLimitExceededError,
)
from langchain.messages import HumanMessage
from langgraph.types import Command
from pydantic import ValidationError

from customer_support_pilot.agents import build_support_agent
from customer_support_pilot.approvals import review_ticket_update
from customer_support_pilot.context import SupportContext
from customer_support_pilot.persistence import (
    build_thread_config,
    open_checkpointer,
    open_database_pool,
)
from customer_support_pilot.repositories import TicketRepository


def show_conversation(conversation_id: UUID, department: str) -> None:
    print(f"\nConversation ID: {conversation_id}")
    print(f"Department: {department}")
    print(
        "Resume command: uv run customer-support-pilot "
        f"--resume {conversation_id}"
    )


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "--resume",
        type=UUID,
        metavar="CONVERSATION_ID",
        help="Resume a saved conversation for the current employee.",
    )
    args = parser.parse_args()

    load_dotenv()

    with (
        open_checkpointer() as checkpointer,
        open_database_pool() as database_pool,
    ):
        context = SupportContext(
            employee_id="FOX-E1001",
            role="support_agent",
            allowed_customer_ids=frozenset(
                {"FOX-C1001", "FOX-C1002"}
            ),
            ticket_repository=TicketRepository(database_pool),
        )

        agent = build_support_agent(checkpointer)
        conversation_id = args.resume or uuid4()
        config = build_thread_config(conversation_id, context)
        snapshot = agent.get_state(config)

        if args.resume and not snapshot.values:
            parser.error(
                "No saved conversation found for this employee "
                "and access settings."
            )

        blocked = bool(snapshot.next) and not snapshot.interrupts

        print("Fox Insurance Service — Customer Support")
        print("Type /new for a new conversation or /exit to quit.")
        show_conversation(
            conversation_id,
            snapshot.values.get("active_department", "triage"),
        )

        while True:
            snapshot = agent.get_state(config)

            if snapshot.interrupts and not blocked:
                pending = snapshot.interrupts[0]
                decision = review_ticket_update(pending, context)

                if decision is None:
                    print("The proposal remains pending.")
                    show_conversation(
                        conversation_id,
                        snapshot.values.get("active_department", "triage"),
                    )
                    return

                invocation = Command(
                    resume={pending.id: decision}
                )
            else:
                try:
                    user_input = input("\nYou: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nGoodbye.")
                    break

                if not user_input:
                    continue

                if user_input.lower() in {"exit", "/exit"}:
                    print("Goodbye.")
                    break

                if user_input.lower() == "/new":
                    conversation_id = uuid4()
                    config = build_thread_config(
                        conversation_id, context
                    )
                    blocked = False
                    print("Started a new conversation.")
                    show_conversation(conversation_id, "triage")
                    continue

                if blocked or snapshot.next:
                    print(
                        "This run cannot accept new messages. "
                        "Enter /new or /exit."
                    )
                    continue

                invocation = {
                    "messages": [HumanMessage(content=user_input)]
                }

            try:
                output = agent.invoke(
                    invocation,
                    config=config,
                    context=context,
                    version="v2",
                )
            except (
                ToolCallLimitExceededError,
                ModelCallLimitExceededError,
            ):
                blocked = True
                print(
                    "\nAssistant: This run reached its processing limit. "
                    "Enter /new or /exit."
                )
                continue
            except ValidationError as error:
                print(f"Validation failed: {error}")
                continue

            if output.interrupts:
                continue

            result = output.value
            response = result["structured_response"]
            department = result.get("active_department", "triage")

            print(f"\nDepartment: {department}")
            print(f"Category: {response.category}")
            print(f"Customer ID: {response.customer_id}")
            print(f"Assistant: {response.answer}")


if __name__ == "__main__":
    main()