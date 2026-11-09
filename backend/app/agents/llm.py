"""Shared LangChain integration for Gemini-backed agents."""

from __future__ import annotations

from app.core.config import get_settings


def build_chat_model(*, temperature: float = 0.2, max_tokens: int = 1024):
    """Create a LangChain chat model configured for Gemini."""
    settings = get_settings()
    if not settings.has_gemini:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=temperature,
        max_output_tokens=max_tokens,
    )


async def invoke_chat(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.2,
    max_tokens: int = 1024,
) -> str:
    """Invoke Gemini through LangChain and return its text response."""
    from langchain_core.messages import HumanMessage, SystemMessage

    response = await build_chat_model(
        temperature=temperature,
        max_tokens=max_tokens,
    ).ainvoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )
    if isinstance(response.content, str):
        return response.content
    return "".join(
        part.get("text", "")
        for part in response.content
        if isinstance(part, dict)
    )
