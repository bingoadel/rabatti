from unittest.mock import MagicMock, patch

from agents import FunctionTool

from models.Tools.historian_greeting_tool import HistorianGreetingTool
from models.agentservice.question_agent import QuestionAgent


def test_historian_greeting_tool_returns_fixed_text() -> None:
    """The tool returns only the fixed sign-off text."""
    assert HistorianGreetingTool().get_text() == "Viele Grüße Dein Hsitoriker"


def test_agent_receives_greeting_tool_via_function_tool(monkeypatch) -> None:
    """The class method is wrapped with function_tool and passed to the agent."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    agent = QuestionAgent(api_key="", model="gpt-4o-mini")

    assert len(agent.sdk_agent.tools) == 1
    tool = agent.sdk_agent.tools[0]
    assert isinstance(tool, FunctionTool)
    assert tool is agent.greeting_function_tool
    assert tool.name == "historian_greeting"


def test_answer_uses_runner_when_api_key_available(monkeypatch) -> None:
    """Should run the SDK agent and append the tool text to the model answer."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    fake_result = MagicMock()
    fake_result.final_output = "Antwort von OpenAI"

    with patch("models.agentservice.question_agent.Runner.run_sync", return_value=fake_result) as run_sync:
        agent = QuestionAgent(api_key="test-key", model="gpt-4o-mini")
        result = agent.answer("Was ist Django?")

    run_sync.assert_called_once_with(agent.sdk_agent, "Was ist Django?")
    assert result == "Antwort von OpenAI\n\nViele Grüße Dein Hsitoriker"


def test_answer_returns_fallback_when_api_key_missing(monkeypatch) -> None:
    """Should return the fallback without crashing if no API key is configured."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    agent = QuestionAgent(api_key="", fallback_answer="Fallback-Text")

    assert agent.answer("Hallo") == "Fallback-Text\n\nViele Grüße Dein Hsitoriker"
