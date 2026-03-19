from typing import List

from app import schemas
from app.core.config import settings
from app.core.openai_client import get_openai_client
from app.core.timeline import TimelineBuilder


def chat_with_llm(payload: schemas.ChatRequest, timeline: TimelineBuilder) -> str:
    """
    Thin wrapper over the OpenAI chat completion API.

    - Uses your existing OpenAI client (app.core.openai_client).
    - Applies a NovaMind-specific system prompt.
    - Logs the call into the timeline.
    """
    timeline.add_step("llm_call", "Calling base LLM for response.")

    client = get_openai_client()

    # Convert pydantic models to raw dicts:
    messages: List[dict] = [
        {"role": m.role, "content": m.content}
        for m in payload.messages
    ]

    system_prompt = (
        "You are NovaMind OS, a personal AI assistant built by Abhay. "
        f"Current Mode: {payload.mode.upper()}. "
        "Be concise but structured. Use bullet points and clear steps. "
        "When relevant, think in terms of tasks, plans, and next actions, "
        "not just chat replies."
    )

    # Prepend system message
    messages.insert(0, {"role": "system", "content": system_prompt})

    resp = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        temperature=0.3,
    )

    return resp.choices[0].message.content or ""
