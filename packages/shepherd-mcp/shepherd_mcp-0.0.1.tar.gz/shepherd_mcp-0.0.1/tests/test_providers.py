"""Tests for provider base classes and AIOBS provider."""

from unittest.mock import Mock, patch

import pytest

from shepherd_mcp.models.aiobs import (
    Event,
    FunctionEvent,
    Session,
    SessionsResponse,
)
from shepherd_mcp.providers.aiobs import (
    AIOBSClient,
    eval_is_failed,
    filter_sessions,
    parse_date,
    session_has_errors,
    session_has_failed_evals,
    session_has_function,
    session_has_model,
    session_has_provider,
    session_matches_labels,
    session_matches_query,
)
from shepherd_mcp.providers.base import (
    AuthenticationError,
    NotFoundError,
    ProviderError,
    RateLimitError,
)

# ============================================================================
# Base Provider Tests
# ============================================================================


class TestExceptions:
    """Tests for provider exceptions."""

    def test_provider_error_is_exception(self):
        with pytest.raises(ProviderError):
            raise ProviderError("test error")

    def test_authentication_error_is_provider_error(self):
        with pytest.raises(ProviderError):
            raise AuthenticationError("auth failed")

    def test_not_found_error_is_provider_error(self):
        with pytest.raises(ProviderError):
            raise NotFoundError("not found")

    def test_rate_limit_error_is_provider_error(self):
        with pytest.raises(ProviderError):
            raise RateLimitError("rate limited")


# ============================================================================
# AIOBS Provider Tests
# ============================================================================


class TestAIOBSClientInit:
    """Tests for AIOBSClient initialization."""

    def test_missing_api_key_raises_error(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(AuthenticationError) as exc_info:
                AIOBSClient()
            assert "AIOBS_API_KEY" in str(exc_info.value)

    def test_init_with_env_var(self):
        with patch.dict("os.environ", {"AIOBS_API_KEY": "test-key"}):
            client = AIOBSClient()
            assert client.api_key == "test-key"
            assert "shepherd-api" in client.endpoint
            client.close()

    def test_init_with_explicit_key(self):
        client = AIOBSClient(api_key="explicit-key")
        assert client.api_key == "explicit-key"
        client.close()

    def test_init_with_custom_endpoint(self):
        client = AIOBSClient(
            api_key="test-key",
            endpoint="https://custom-api.example.com/",
        )
        assert client.endpoint == "https://custom-api.example.com"  # trailing slash removed
        client.close()

    def test_provider_name(self):
        client = AIOBSClient(api_key="test-key")
        assert client.name == "aiobs"
        client.close()


class TestAIOBSClientContextManager:
    """Tests for AIOBSClient context manager."""

    def test_context_manager(self):
        with AIOBSClient(api_key="test-key") as client:
            assert client.name == "aiobs"


class TestAIOBSClientErrorHandling:
    """Tests for AIOBSClient error handling."""

    def setup_method(self):
        self.client = AIOBSClient(api_key="test-key")

    def teardown_method(self):
        self.client.close()

    def test_401_raises_authentication_error(self):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid API key"}
        with pytest.raises(AuthenticationError) as exc_info:
            self.client._handle_error_response(mock_response)
        assert "Invalid API key" in str(exc_info.value)

    def test_404_raises_not_found_error(self):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Session not found"}
        with pytest.raises(NotFoundError) as exc_info:
            self.client._handle_error_response(mock_response)
        assert "Session not found" in str(exc_info.value)

    def test_500_raises_provider_error(self):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"detail": "Internal error"}
        with pytest.raises(ProviderError) as exc_info:
            self.client._handle_error_response(mock_response)
        assert "Internal error" in str(exc_info.value)


# ============================================================================
# Parse Date Tests
# ============================================================================


class TestParseDate:
    """Tests for parse_date function."""

    def test_date_only(self):
        result = parse_date("2025-01-15")
        # Should be a Unix timestamp
        assert isinstance(result, float)
        assert result > 0

    def test_datetime_with_time(self):
        result = parse_date("2025-01-15 12:30:45")
        assert isinstance(result, float)

    def test_datetime_iso_format(self):
        result = parse_date("2025-01-15T12:30:45")
        assert isinstance(result, float)

    def test_datetime_short(self):
        result = parse_date("2025-01-15 12:30")
        assert isinstance(result, float)

    def test_invalid_format_raises_error(self):
        with pytest.raises(ValueError) as exc_info:
            parse_date("invalid-date")
        assert "Invalid date format" in str(exc_info.value)


# ============================================================================
# Session Filtering Tests
# ============================================================================


def make_session(
    id: str = "test-session",
    name: str = "Test Session",
    started_at: float = 1735689600.0,
    labels: dict = None,
    meta: dict = None,
) -> Session:
    """Helper to create Session objects for testing."""
    return Session(
        id=id,
        name=name,
        started_at=started_at,
        ended_at=started_at + 60,
        labels=labels or {},
        meta=meta or {},
    )


def make_event(
    session_id: str = "test-session",
    provider: str = "openai",
    model: str = "gpt-4o-mini",
    error: str = None,
    evaluations: list = None,
) -> Event:
    """Helper to create Event objects for testing."""
    return Event(
        provider=provider,
        api="chat.completions.create",
        request={"model": model},
        response=None,
        error=error,
        started_at=1735689600.0,
        ended_at=1735689601.0,
        duration_ms=1000.0,
        span_id="span-1",
        session_id=session_id,
        evaluations=evaluations or [],
    )


def make_function_event(
    session_id: str = "test-session",
    name: str = "my_function",
    module: str = "my_module",
    error: str = None,
    evaluations: list = None,
) -> FunctionEvent:
    """Helper to create FunctionEvent objects for testing."""
    return FunctionEvent(
        provider="function",
        api="call",
        name=name,
        module=module,
        error=error,
        started_at=1735689600.0,
        ended_at=1735689601.0,
        duration_ms=1000.0,
        span_id="span-1",
        session_id=session_id,
        evaluations=evaluations or [],
    )


class TestSessionMatchesQuery:
    """Tests for session_matches_query."""

    def test_matches_id(self):
        session = make_session(id="abc-123-def")
        assert session_matches_query(session, "abc-123") is True

    def test_matches_name(self):
        session = make_session(name="Production Run")
        assert session_matches_query(session, "production") is True

    def test_matches_label_value(self):
        session = make_session(labels={"env": "staging"})
        assert session_matches_query(session, "staging") is True

    def test_matches_meta_value(self):
        session = make_session(meta={"user": "john@example.com"})
        assert session_matches_query(session, "john") is True

    def test_no_match(self):
        session = make_session(id="abc", name="Test", labels={}, meta={})
        assert session_matches_query(session, "xyz") is False


class TestSessionMatchesLabels:
    """Tests for session_matches_labels."""

    def test_matches_all_labels(self):
        session = make_session(labels={"env": "prod", "team": "ml"})
        assert session_matches_labels(session, {"env": "prod", "team": "ml"}) is True

    def test_matches_subset(self):
        session = make_session(labels={"env": "prod", "team": "ml"})
        assert session_matches_labels(session, {"env": "prod"}) is True

    def test_missing_label(self):
        session = make_session(labels={"env": "prod"})
        assert session_matches_labels(session, {"team": "ml"}) is False

    def test_wrong_value(self):
        session = make_session(labels={"env": "prod"})
        assert session_matches_labels(session, {"env": "staging"}) is False


class TestSessionHasProvider:
    """Tests for session_has_provider."""

    def test_matches_provider(self):
        session = make_session(id="s1")
        events = [make_event(session_id="s1", provider="openai")]
        assert session_has_provider(session, events, [], "openai") is True

    def test_case_insensitive(self):
        session = make_session(id="s1")
        events = [make_event(session_id="s1", provider="OpenAI")]
        assert session_has_provider(session, events, [], "OPENAI") is True

    def test_no_match(self):
        session = make_session(id="s1")
        events = [make_event(session_id="s1", provider="anthropic")]
        assert session_has_provider(session, events, [], "openai") is False

    def test_matches_in_function_events(self):
        session = make_session(id="s1")
        fn_events = [make_function_event(session_id="s1")]
        fn_events[0].provider = "custom"
        assert session_has_provider(session, [], fn_events, "custom") is True


class TestSessionHasModel:
    """Tests for session_has_model."""

    def test_matches_model(self):
        session = make_session(id="s1")
        events = [make_event(session_id="s1", model="gpt-4o-mini")]
        assert session_has_model(session, events, "gpt-4o") is True

    def test_case_insensitive(self):
        session = make_session(id="s1")
        events = [make_event(session_id="s1", model="GPT-4o-Mini")]
        assert session_has_model(session, events, "gpt-4o-mini") is True

    def test_no_match(self):
        session = make_session(id="s1")
        events = [make_event(session_id="s1", model="claude-3")]
        assert session_has_model(session, events, "gpt-4") is False


class TestSessionHasErrors:
    """Tests for session_has_errors."""

    def test_event_with_error(self):
        session = make_session(id="s1")
        events = [make_event(session_id="s1", error="API error")]
        assert session_has_errors(session, events, []) is True

    def test_function_event_with_error(self):
        session = make_session(id="s1")
        fn_events = [make_function_event(session_id="s1", error="Function failed")]
        assert session_has_errors(session, [], fn_events) is True

    def test_no_errors(self):
        session = make_session(id="s1")
        events = [make_event(session_id="s1")]
        fn_events = [make_function_event(session_id="s1")]
        assert session_has_errors(session, events, fn_events) is False


class TestSessionHasFunction:
    """Tests for session_has_function."""

    def test_matches_function_name(self):
        session = make_session(id="s1")
        fn_events = [make_function_event(session_id="s1", name="process_data")]
        assert session_has_function(session, fn_events, "process") is True

    def test_matches_module_name(self):
        session = make_session(id="s1")
        fn_events = [make_function_event(session_id="s1", module="data_pipeline")]
        assert session_has_function(session, fn_events, "pipeline") is True

    def test_no_match(self):
        session = make_session(id="s1")
        fn_events = [make_function_event(session_id="s1", name="func_a")]
        assert session_has_function(session, fn_events, "func_b") is False


class TestEvalIsFailed:
    """Tests for eval_is_failed."""

    def test_passed_false(self):
        assert eval_is_failed({"passed": False}) is True

    def test_passed_true(self):
        assert eval_is_failed({"passed": True}) is False

    def test_result_false(self):
        assert eval_is_failed({"result": False}) is True

    def test_status_failed(self):
        assert eval_is_failed({"status": "failed"}) is True
        assert eval_is_failed({"status": "fail"}) is True
        assert eval_is_failed({"status": "error"}) is True

    def test_success_false(self):
        assert eval_is_failed({"success": False}) is True

    def test_not_dict(self):
        assert eval_is_failed("not a dict") is False
        assert eval_is_failed(None) is False


class TestSessionHasFailedEvals:
    """Tests for session_has_failed_evals."""

    def test_event_with_failed_eval(self):
        session = make_session(id="s1")
        events = [make_event(session_id="s1", evaluations=[{"passed": False}])]
        assert session_has_failed_evals(session, events, []) is True

    def test_function_event_with_failed_eval(self):
        session = make_session(id="s1")
        fn_events = [make_function_event(session_id="s1", evaluations=[{"passed": False}])]
        assert session_has_failed_evals(session, [], fn_events) is True

    def test_no_failed_evals(self):
        session = make_session(id="s1")
        events = [make_event(session_id="s1", evaluations=[{"passed": True}])]
        assert session_has_failed_evals(session, events, []) is False


class TestFilterSessions:
    """Tests for filter_sessions function."""

    def setup_method(self):
        self.sessions = [
            make_session(id="s1", name="Production", labels={"env": "prod"}),
            make_session(id="s2", name="Staging", labels={"env": "staging"}),
            make_session(id="s3", name="Development", labels={"env": "dev"}),
        ]
        self.events = [
            make_event(session_id="s1", provider="openai", model="gpt-4"),
            make_event(session_id="s2", provider="anthropic", model="claude-3"),
            make_event(session_id="s3", provider="openai", model="gpt-3.5"),
        ]
        self.response = SessionsResponse(
            sessions=self.sessions,
            events=self.events,
            function_events=[],
        )

    def test_no_filters(self):
        result = filter_sessions(self.response)
        assert len(result.sessions) == 3

    def test_filter_by_query(self):
        result = filter_sessions(self.response, query="prod")
        assert len(result.sessions) == 1
        assert result.sessions[0].id == "s1"

    def test_filter_by_labels(self):
        result = filter_sessions(self.response, labels={"env": "staging"})
        assert len(result.sessions) == 1
        assert result.sessions[0].id == "s2"

    def test_filter_by_provider(self):
        result = filter_sessions(self.response, provider="openai")
        assert len(result.sessions) == 2
        assert "s1" in [s.id for s in result.sessions]
        assert "s3" in [s.id for s in result.sessions]

    def test_filter_by_model(self):
        result = filter_sessions(self.response, model="gpt-4")
        assert len(result.sessions) == 1
        assert result.sessions[0].id == "s1"

    def test_events_filtered_with_sessions(self):
        result = filter_sessions(self.response, query="prod")
        # Events should only include those from matching sessions
        assert len(result.events) == 1
        assert result.events[0].session_id == "s1"
