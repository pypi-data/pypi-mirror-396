"""Tests for the Shepherd MCP server."""

from shepherd_mcp.models.aiobs import Event, Session
from shepherd_mcp.server import (
    calc_avg_latency,
    calc_total_tokens,
    compare_request_params,
    compare_responses,
    compare_system_prompts,
    count_errors,
    extract_request_params,
    extract_responses,
    extract_system_prompts,
    format_duration,
    format_timestamp,
    get_model_distribution,
    get_provider_distribution,
    session_to_dict,
)


class TestFormatTimestamp:
    """Tests for format_timestamp."""

    def test_basic_timestamp(self):
        # Unix timestamp for 2025-01-01 00:00:00 UTC
        ts = 1735689600.0
        result = format_timestamp(ts)
        assert "2025" in result
        assert "01" in result


class TestFormatDuration:
    """Tests for format_duration."""

    def test_milliseconds(self):
        assert format_duration(500) == "500ms"
        assert format_duration(999) == "999ms"

    def test_seconds(self):
        assert format_duration(1000) == "1.0s"
        assert format_duration(5500) == "5.5s"

    def test_minutes(self):
        assert format_duration(60000) == "1.0m"
        assert format_duration(90000) == "1.5m"


class TestSessionToDict:
    """Tests for session_to_dict."""

    def test_basic_session(self):
        session = Session(
            id="test-123",
            name="test-session",
            started_at=1735689600.0,
            ended_at=1735689660.0,
            meta={"cwd": "/test"},
            labels={"env": "test"},
        )
        result = session_to_dict(session, [], [])

        assert result["id"] == "test-123"
        assert result["name"] == "test-session"
        assert result["duration_ms"] == 60000.0
        assert result["duration"] == "1.0m"
        assert result["labels"]["env"] == "test"


class TestCalcTotalTokens:
    """Tests for calc_total_tokens."""

    def test_empty_events(self):
        result = calc_total_tokens([])
        assert result == {"input": 0, "output": 0, "total": 0}


class TestCalcAvgLatency:
    """Tests for calc_avg_latency."""

    def test_empty_events(self):
        result = calc_avg_latency([])
        assert result == 0.0


class TestCountErrors:
    """Tests for count_errors."""

    def test_no_errors(self):
        result = count_errors([], [])
        assert result == 0


class TestGetProviderDistribution:
    """Tests for get_provider_distribution."""

    def test_empty_events(self):
        result = get_provider_distribution([])
        assert result == {}


class TestGetModelDistribution:
    """Tests for get_model_distribution."""

    def test_empty_events(self):
        result = get_model_distribution([])
        assert result == {}


# ============================================================================
# Tests for new comparison functions
# ============================================================================


def make_event(
    provider: str = "openai",
    api: str = "chat.completions.create",
    request: dict = None,
    response: dict = None,
    error: str = None,
    session_id: str = "test-session",
    span_id: str = "span-1",
) -> Event:
    """Helper to create Event objects for testing."""
    return Event(
        provider=provider,
        api=api,
        request=request or {},
        response=response,
        error=error,
        started_at=1735689600.0,
        ended_at=1735689601.0,
        duration_ms=1000.0,
        span_id=span_id,
        session_id=session_id,
    )


class TestExtractSystemPrompts:
    """Tests for extract_system_prompts."""

    def test_empty_events(self):
        result = extract_system_prompts([])
        assert result == []

    def test_openai_format_system_message(self):
        """Test extracting system prompt from OpenAI-style messages array."""
        event = make_event(
            request={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello"},
                ],
            }
        )
        result = extract_system_prompts([event])

        assert len(result) == 1
        assert result[0]["provider"] == "openai"
        assert result[0]["model"] == "gpt-4o-mini"
        assert result[0]["content"] == "You are a helpful assistant."
        assert result[0]["full_length"] == len("You are a helpful assistant.")

    def test_anthropic_format_system_param(self):
        """Test extracting system prompt from Anthropic-style top-level system param."""
        event = make_event(
            provider="anthropic",
            request={
                "model": "claude-3-sonnet",
                "system": "You are Claude, a helpful AI assistant.",
                "messages": [{"role": "user", "content": "Hello"}],
            },
        )
        result = extract_system_prompts([event])

        assert len(result) == 1
        assert result[0]["provider"] == "anthropic"
        assert result[0]["model"] == "claude-3-sonnet"
        assert result[0]["content"] == "You are Claude, a helpful AI assistant."

    def test_no_system_prompt(self):
        """Test event without system prompt."""
        event = make_event(
            request={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello"}],
            }
        )
        result = extract_system_prompts([event])
        assert result == []

    def test_content_blocks_format(self):
        """Test system prompt with content blocks (Anthropic format)."""
        event = make_event(
            provider="anthropic",
            request={
                "model": "claude-3",
                "messages": [
                    {
                        "role": "system",
                        "content": [
                            {"type": "text", "text": "Part 1."},
                            {"type": "text", "text": "Part 2."},
                        ],
                    },
                    {"role": "user", "content": "Hello"},
                ],
            },
        )
        result = extract_system_prompts([event])

        assert len(result) == 1
        assert result[0]["content"] == "Part 1. Part 2."

    def test_long_content_truncated(self):
        """Test that long system prompts are truncated in content field."""
        long_prompt = "x" * 600
        event = make_event(
            request={
                "model": "gpt-4",
                "messages": [{"role": "system", "content": long_prompt}],
            }
        )
        result = extract_system_prompts([event])

        assert len(result) == 1
        assert result[0]["full_length"] == 600
        assert len(result[0]["content"]) == 503  # 500 + "..."
        assert result[0]["content"].endswith("...")


class TestCompareSystemPrompts:
    """Tests for compare_system_prompts."""

    def test_empty_prompts(self):
        result = compare_system_prompts([], [])
        assert result["changed"] is False
        assert result["unique_to_session1"] == []
        assert result["unique_to_session2"] == []
        assert result["common"] == []

    def test_identical_prompts(self):
        prompts = [{"content": "You are helpful.", "provider": "openai", "model": "gpt-4"}]
        result = compare_system_prompts(prompts, prompts)

        assert result["changed"] is False
        assert "You are helpful." in result["common"]

    def test_different_prompts(self):
        prompts1 = [{"content": "You are helpful.", "provider": "openai", "model": "gpt-4"}]
        prompts2 = [{"content": "You are an expert.", "provider": "openai", "model": "gpt-4"}]
        result = compare_system_prompts(prompts1, prompts2)

        assert result["changed"] is True
        assert "You are helpful." in result["unique_to_session1"]
        assert "You are an expert." in result["unique_to_session2"]
        assert result["common"] == []

    def test_added_prompt(self):
        prompts1 = [{"content": "Prompt A", "provider": "openai", "model": "gpt-4"}]
        prompts2 = [
            {"content": "Prompt A", "provider": "openai", "model": "gpt-4"},
            {"content": "Prompt B", "provider": "openai", "model": "gpt-4"},
        ]
        result = compare_system_prompts(prompts1, prompts2)

        assert result["changed"] is True
        assert "Prompt A" in result["common"]
        assert "Prompt B" in result["unique_to_session2"]


class TestExtractRequestParams:
    """Tests for extract_request_params."""

    def test_empty_events(self):
        result = extract_request_params([])
        assert result == []

    def test_basic_params(self):
        event = make_event(
            request={
                "model": "gpt-4o-mini",
                "temperature": 0.7,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": "Hello world"}],
            }
        )
        result = extract_request_params([event])

        assert len(result) == 1
        assert result[0]["model"] == "gpt-4o-mini"
        assert result[0]["temperature"] == 0.7
        assert result[0]["max_tokens"] == 1000
        assert result[0]["user_message_preview"] == "Hello world"

    def test_tools_summarized(self):
        """Test that tools are summarized to just function names."""
        event = make_event(
            request={
                "model": "gpt-4",
                "tools": [
                    {"function": {"name": "get_weather", "parameters": {"type": "object"}}},
                    {"function": {"name": "search", "parameters": {"type": "object"}}},
                ],
            }
        )
        result = extract_request_params([event])

        assert result[0]["tools"] == ["get_weather", "search"]

    def test_streaming_flag(self):
        event = make_event(request={"model": "gpt-4", "stream": True})
        result = extract_request_params([event])

        assert result[0]["stream"] is True

    def test_user_message_preview_truncated(self):
        """Test that long user messages are truncated."""
        long_message = "y" * 300
        event = make_event(
            request={
                "model": "gpt-4",
                "messages": [{"role": "user", "content": long_message}],
            }
        )
        result = extract_request_params([event])

        assert len(result[0]["user_message_preview"]) == 203  # 200 + "..."
        assert result[0]["user_message_preview"].endswith("...")


class TestCompareRequestParams:
    """Tests for compare_request_params."""

    def test_empty_params(self):
        result = compare_request_params([], [])

        assert result["session1"]["summary"]["avg_temperature"] is None
        assert result["session2"]["summary"]["avg_temperature"] is None
        assert result["tools_added"] == []
        assert result["tools_removed"] == []

    def test_temperature_comparison(self):
        params1 = [{"temperature": 0.5, "model": "gpt-4"}]
        params2 = [{"temperature": 0.9, "model": "gpt-4"}]
        result = compare_request_params(params1, params2)

        assert result["session1"]["summary"]["avg_temperature"] == 0.5
        assert result["session2"]["summary"]["avg_temperature"] == 0.9

    def test_tools_added_removed(self):
        params1 = [{"model": "gpt-4", "tools": ["tool_a", "tool_b"]}]
        params2 = [{"model": "gpt-4", "tools": ["tool_b", "tool_c"]}]
        result = compare_request_params(params1, params2)

        assert "tool_a" in result["tools_removed"]
        assert "tool_c" in result["tools_added"]

    def test_streaming_count(self):
        params1 = [
            {"model": "gpt-4", "stream": True},
            {"model": "gpt-4", "stream": False},
        ]
        params2 = [
            {"model": "gpt-4", "stream": True},
            {"model": "gpt-4", "stream": True},
        ]
        result = compare_request_params(params1, params2)

        assert result["session1"]["summary"]["streaming_requests"] == 1
        assert result["session2"]["summary"]["streaming_requests"] == 2


class TestExtractResponses:
    """Tests for extract_responses."""

    def test_empty_events(self):
        result = extract_responses([])
        assert result == []

    def test_openai_format_response(self):
        """Test extracting response in OpenAI format."""
        event = make_event(
            request={"model": "gpt-4o-mini"},
            response={
                "model": "gpt-4o-mini-2024-07-18",
                "choices": [
                    {
                        "message": {"content": "Hello! How can I help you?"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 8,
                    "total_tokens": 18,
                },
            },
        )
        result = extract_responses([event])

        assert len(result) == 1
        assert result[0]["model"] == "gpt-4o-mini-2024-07-18"
        assert result[0]["content_preview"] == "Hello! How can I help you?"
        assert result[0]["content_length"] == 26
        assert result[0]["tokens"]["input"] == 10
        assert result[0]["tokens"]["output"] == 8
        assert result[0]["stop_reason"] == "stop"

    def test_anthropic_format_response(self):
        """Test extracting response in Anthropic format."""
        event = make_event(
            provider="anthropic",
            request={"model": "claude-3-sonnet"},
            response={
                "model": "claude-3-sonnet-20240229",
                "content": [{"type": "text", "text": "I'm Claude, happy to help!"}],
                "stop_reason": "end_turn",
                "usage": {"input_tokens": 15, "output_tokens": 10},
            },
        )
        result = extract_responses([event])

        assert len(result) == 1
        assert result[0]["content_preview"] == "I'm Claude, happy to help!"
        assert result[0]["stop_reason"] == "end_turn"
        assert result[0]["tokens"]["input"] == 15
        assert result[0]["tokens"]["output"] == 10

    def test_tool_calls_openai(self):
        """Test extracting tool calls from OpenAI response."""
        event = make_event(
            response={
                "model": "gpt-4",
                "choices": [
                    {
                        "message": {
                            "content": None,
                            "tool_calls": [
                                {
                                    "function": {
                                        "name": "get_weather",
                                        "arguments": '{"location": "NYC"}',
                                    }
                                }
                            ],
                        },
                        "finish_reason": "tool_calls",
                    }
                ],
            },
        )
        result = extract_responses([event])

        assert len(result) == 1
        assert len(result[0]["tool_calls"]) == 1
        assert result[0]["tool_calls"][0]["name"] == "get_weather"
        assert "NYC" in result[0]["tool_calls"][0]["arguments_preview"]

    def test_tool_use_anthropic(self):
        """Test extracting tool use from Anthropic response."""
        event = make_event(
            provider="anthropic",
            response={
                "model": "claude-3",
                "content": [{"type": "tool_use", "name": "calculator", "input": {"expr": "2+2"}}],
            },
        )
        result = extract_responses([event])

        assert len(result) == 1
        assert len(result[0]["tool_calls"]) == 1
        assert result[0]["tool_calls"][0]["name"] == "calculator"

    def test_content_preview_truncated(self):
        """Test that long content is truncated."""
        long_content = "z" * 400
        event = make_event(
            response={
                "model": "gpt-4",
                "choices": [{"message": {"content": long_content}}],
            },
        )
        result = extract_responses([event])

        assert result[0]["content_length"] == 400
        assert len(result[0]["content_preview"]) == 303  # 300 + "..."


class TestCompareResponses:
    """Tests for compare_responses."""

    def test_empty_responses(self):
        result = compare_responses([], [])

        assert result["session1"]["summary"]["total_content_length"] == 0
        assert result["session1"]["summary"]["avg_content_length"] == 0
        assert result["delta"]["avg_content_length"] == 0

    def test_content_length_comparison(self):
        responses1 = [{"content_length": 100}, {"content_length": 200}]
        responses2 = [{"content_length": 300}, {"content_length": 400}]
        result = compare_responses(responses1, responses2)

        assert result["session1"]["summary"]["total_content_length"] == 300
        assert result["session1"]["summary"]["avg_content_length"] == 150.0
        assert result["session2"]["summary"]["total_content_length"] == 700
        assert result["session2"]["summary"]["avg_content_length"] == 350.0
        assert result["delta"]["avg_content_length"] == 200.0

    def test_tool_call_count(self):
        responses1 = [{"tool_calls": [{"name": "a"}]}]
        responses2 = [{"tool_calls": [{"name": "a"}, {"name": "b"}]}]
        result = compare_responses(responses1, responses2)

        assert result["session1"]["summary"]["tool_call_count"] == 1
        assert result["session2"]["summary"]["tool_call_count"] == 2
        assert result["delta"]["tool_call_count"] == 1

    def test_stop_reasons_distribution(self):
        responses1 = [
            {"stop_reason": "stop"},
            {"stop_reason": "stop"},
            {"stop_reason": "length"},
        ]
        responses2 = [{"stop_reason": "tool_calls"}]
        result = compare_responses(responses1, responses2)

        assert result["session1"]["summary"]["stop_reasons"]["stop"] == 2
        assert result["session1"]["summary"]["stop_reasons"]["length"] == 1
        assert result["session2"]["summary"]["stop_reasons"]["tool_calls"] == 1
