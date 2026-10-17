from uuid import uuid4

from dotenv import load_dotenv
from langchain.messages import HumanMessage

from customer_support_pilot.agents import build_support_agent
from customer_support_pilot.context import SupportContext
from langchain.agents.middleware.model_call_limit import (
    ModelCallLimitExceededError,
)
from langchain.agents.middleware.tool_call_limit import (
    ToolCallLimitExceededError,
)


def main() -> None:
    load_dotenv()

    agent = build_support_agent()
    context = SupportContext(
        employee_id="FOX-E1001",
        role="support_agent",
        allowed_customer_ids=frozenset(
            {"FOX-C1001", "FOX-C1002"}
        ),
    )
    config = {"configurable": {"thread_id": str(uuid4())}}

    print("Fox Insurance Service — Customer Support")
    print("Type /new for a new conversation or /exit to quit.")
    
    requires_new_conversation = False
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
            config = {"configurable": {"thread_id": str(uuid4())}}
            requires_new_conversation = False
            print("Started a new conversation.")
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
                "\nAssistant: This request reached the customer lookup "
                "limit. No additional lookup was performed. "
                "Enter /new to start a new conversation "
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