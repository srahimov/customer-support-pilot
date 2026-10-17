from langchain.chat_models import init_chat_model
import os 

def create_chat_model():
    model = init_chat_model(
        model=os.getenv("OPENAI_MODEL") or "gpt-6-luna",
        model_provider="openai",
        use_responses_api=True,
        reasoning_effort="low",
        timeout=30,
        max_retries=2,
    )
    return model