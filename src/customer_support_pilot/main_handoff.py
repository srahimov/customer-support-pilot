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

from customer_support_pilot.agents import build_support_agent
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

        requires_new_conversation = bool(snapshot.next)
        department = snapshot.values.get("active_department", "triage")

        print("Fox Insurance Service — Customer Support")
        print("Type /new for a new conversation or /exit to quit.")
        show_conversation(conversation_id, department)

        if requires_new_conversation:
            print("This conversation has an unfinished run. Enter /new.")

        while True:
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
                config = build_thread_config(conversation_id, context)
                requires_new_conversation = False
                print("Started a new conversation.")
                show_conversation(conversation_id, "triage")
                continue

            if requires_new_conversation:
                print(
                    "\nAssistant: Please enter /new to continue "
                    "or /exit to quit."
                )
                continue

            try:
                result = agent.invoke(
                    {"messages": [HumanMessage(content=user_input)]},
                    config=config,
                    context=context,
                )
            except ToolCallLimitExceededError:
                requires_new_conversation = True
                print(
                    "\nAssistant: This request reached the account lookup "
                    "limit. Enter /new to start a new conversation "
                    "or /exit to quit."
                )
                continue
            except ModelCallLimitExceededError:
                requires_new_conversation = True
                print(
                    "\nAssistant: This request reached its processing limit. "
                    "Enter /new to start a new conversation "
                    "or /exit to quit."
                )
                continue

            response = result["structured_response"]
            department = result.get("active_department", "triage")

            print(f"\nDepartment: {department}")
            print(f"Category: {response.category}")
            print(f"Customer ID: {response.customer_id}")
            print(f"Assistant: {response.answer}")


if __name__ == "__main__":
    main()