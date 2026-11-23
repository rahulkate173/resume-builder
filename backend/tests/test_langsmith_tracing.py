import importlib
import os
from unittest.mock import Mock

import pytest
from dotenv import main as dotenv_main
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from langsmith import tracing_context
from langsmith.utils import tracing_is_enabled

from app.agents import llm


class _RecordingLangSmithClient:
    otel_exporter = None

    def __init__(self):
        self.created_runs = []
        self.updated_runs = []

    def create_run(self, **kwargs):
        self.created_runs.append(kwargs)

    def update_run(self, **kwargs):
        self.updated_runs.append(kwargs)


@pytest.mark.asyncio
async def test_dotenv_enables_langsmith_tracing_for_langchain_calls(
    monkeypatch, tmp_path
):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "LANGSMITH_TRACING=true\nLANGSMITH_API_KEY=test-key\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        dotenv_main, "find_dotenv", Mock(return_value=str(env_file))
    )
    monkeypatch.delenv("LANGSMITH_TRACING", raising=False)
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGCHAIN_TRACING_V2", raising=False)

    import app

    importlib.reload(app)
    assert os.environ["LANGSMITH_TRACING"] == "true"
    assert os.environ["LANGSMITH_API_KEY"] == "test-key"

    def fake_chat(messages):
        assert [message.content for message in messages] == [
            "system prompt",
            "user prompt",
        ]
        return AIMessage(content="trace-check")

    model = RunnableLambda(fake_chat)
    monkeypatch.setattr(llm, "build_chat_model", lambda **_kwargs: model)
    client = _RecordingLangSmithClient()

    with tracing_context(client=client, enabled=True):
        assert tracing_is_enabled() is True
        response = await llm.invoke_chat("system prompt", "user prompt")

    assert response == "trace-check"
    assert len(client.created_runs) == 1
    assert client.created_runs[0]["name"]
    assert len(client.updated_runs) == 1