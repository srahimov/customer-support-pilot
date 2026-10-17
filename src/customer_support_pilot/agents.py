from langchain.agents import create_agent
from langgraph.checkpoint.base import BaseCheckpointSaver

from customer_support_pilot.context import SupportContext
from customer_support_pilot.middleware import (
    ALL_TOOLS,
    BASE_PROMPT,
    build_support_middleware,
)
from customer_support_pilot.models import create_chat_model
from customer_support_pilot.schemas import SupportResponse
from customer_support_pilot.state import SupportState


def build_support_agent(checkpointer: BaseCheckpointSaver):
    return create_agent(
        model=create_chat_model(),
        tools=ALL_TOOLS,
        system_prompt=BASE_PROMPT,
        state_schema=SupportState,
        context_schema=SupportContext,
        response_format=SupportResponse,
        middleware=build_support_middleware(),
        checkpointer=checkpointer,
    )