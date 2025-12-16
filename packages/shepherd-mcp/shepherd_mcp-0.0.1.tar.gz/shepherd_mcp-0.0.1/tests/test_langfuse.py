"""Tests for Langfuse provider and models."""

from unittest.mock import Mock, patch

import pytest

from shepherd_mcp.models.langfuse import (
    LangfuseObservation,
    LangfuseObservationsResponse,
    LangfuseScore,
    LangfuseScoresResponse,
    LangfuseSession,
    LangfuseSessionsResponse,
    LangfuseTrace,
    LangfuseTracesResponse,
)
from shepherd_mcp.providers.base import (
    AuthenticationError,
    NotFoundError,
    ProviderError,
    RateLimitError,
)
from shepherd_mcp.providers.langfuse import LangfuseClient
from shepherd_mcp.server import (
    _session_matches_query,
    _trace_matches_query,
    format_langfuse_duration,
    handle_langfuse_search_sessions,
    handle_langfuse_search_traces,
    langfuse_observation_to_dict,
    langfuse_session_to_dict,
    langfuse_trace_to_dict,
)

# ============================================================================
# Model Tests
# ============================================================================


class TestLangfuseObservation:
    """Tests for LangfuseObservation model."""

    def test_basic_observation(self):
        obs = LangfuseObservation(
            id="obs-123",
            traceId="trace-456",
            type="GENERATION",
            name="chat-completion",
            startTime="2025-01-01T00:00:00Z",
            endTime="2025-01-01T00:00:01Z",
            model="gpt-4o-mini",
        )
        assert obs.id == "obs-123"
        assert obs.trace_id == "trace-456"
        assert obs.type == "GENERATION"
        assert obs.name == "chat-completion"
        assert obs.model == "gpt-4o-mini"

    def test_observation_with_usage(self):
        obs = LangfuseObservation(
            id="obs-123",
            traceId="trace-456",
            type="GENERATION",
            startTime="2025-01-01T00:00:00Z",
            usage={"input": 100, "output": 50, "total": 150},
            latency=1.5,
        )
        assert obs.usage == {"input": 100, "output": 50, "total": 150}
        assert obs.latency == 1.5

    def test_observation_with_costs(self):
        obs = LangfuseObservation(
            id="obs-123",
            traceId="trace-456",
            type="GENERATION",
            startTime="2025-01-01T00:00:00Z",
            calculatedInputCost=0.001,
            calculatedOutputCost=0.002,
            calculatedTotalCost=0.003,
        )
        assert obs.calculated_input_cost == 0.001
        assert obs.calculated_output_cost == 0.002
        assert obs.calculated_total_cost == 0.003

    def test_observation_with_parent(self):
        obs = LangfuseObservation(
            id="obs-123",
            traceId="trace-456",
            type="SPAN",
            startTime="2025-01-01T00:00:00Z",
            parentObservationId="obs-parent",
        )
        assert obs.parent_observation_id == "obs-parent"

    def test_observation_levels(self):
        for level in ["DEBUG", "DEFAULT", "WARNING", "ERROR"]:
            obs = LangfuseObservation(
                id="obs-123",
                traceId="trace-456",
                type="EVENT",
                startTime="2025-01-01T00:00:00Z",
                level=level,
            )
            assert obs.level == level


class TestLangfuseTrace:
    """Tests for LangfuseTrace model."""

    def test_basic_trace(self):
        trace = LangfuseTrace(
            id="trace-123",
            timestamp="2025-01-01T00:00:00Z",
            name="my-workflow",
        )
        assert trace.id == "trace-123"
        assert trace.name == "my-workflow"
        assert trace.observations == []
        assert trace.tags == []

    def test_trace_with_user_and_session(self):
        trace = LangfuseTrace(
            id="trace-123",
            timestamp="2025-01-01T00:00:00Z",
            userId="user-456",
            sessionId="session-789",
        )
        assert trace.user_id == "user-456"
        assert trace.session_id == "session-789"

    def test_trace_with_metadata(self):
        trace = LangfuseTrace(
            id="trace-123",
            timestamp="2025-01-01T00:00:00Z",
            metadata={"env": "production", "version": "1.0"},
            tags=["important", "test"],
        )
        assert trace.metadata == {"env": "production", "version": "1.0"}
        assert trace.tags == ["important", "test"]

    def test_trace_with_cost_and_latency(self):
        trace = LangfuseTrace(
            id="trace-123",
            timestamp="2025-01-01T00:00:00Z",
            latency=2.5,
            totalCost=0.05,
        )
        assert trace.latency == 2.5
        assert trace.total_cost == 0.05

    def test_trace_with_observation_ids(self):
        trace = LangfuseTrace(
            id="trace-123",
            timestamp="2025-01-01T00:00:00Z",
            observations=["obs-1", "obs-2", "obs-3"],
        )
        assert len(trace.observations) == 3
        assert "obs-1" in trace.observations


class TestLangfuseSession:
    """Tests for LangfuseSession model."""

    def test_basic_session(self):
        session = LangfuseSession(
            id="session-123",
            createdAt="2025-01-01T00:00:00Z",
            projectId="project-456",
        )
        assert session.id == "session-123"
        assert session.created_at == "2025-01-01T00:00:00Z"
        assert session.project_id == "project-456"

    def test_session_with_metrics(self):
        session = LangfuseSession(
            id="session-123",
            createdAt="2025-01-01T00:00:00Z",
            projectId="project-456",
            countTraces=5,
            totalCost=0.25,
            totalTokens=5000,
            inputTokens=3000,
            outputTokens=2000,
        )
        assert session.count_traces == 5
        assert session.total_cost == 0.25
        assert session.total_tokens == 5000
        assert session.input_tokens == 3000
        assert session.output_tokens == 2000

    def test_session_with_users(self):
        session = LangfuseSession(
            id="session-123",
            createdAt="2025-01-01T00:00:00Z",
            projectId="project-456",
            userIds=["user-1", "user-2"],
        )
        assert session.user_ids == ["user-1", "user-2"]


class TestLangfuseScore:
    """Tests for LangfuseScore model."""

    def test_numeric_score(self):
        score = LangfuseScore(
            id="score-123",
            traceId="trace-456",
            name="accuracy",
            value=0.95,
            timestamp="2025-01-01T00:00:00Z",
            source="API",
            dataType="NUMERIC",
        )
        assert score.id == "score-123"
        assert score.trace_id == "trace-456"
        assert score.name == "accuracy"
        assert score.value == 0.95
        assert score.data_type == "NUMERIC"

    def test_categorical_score(self):
        score = LangfuseScore(
            id="score-123",
            traceId="trace-456",
            name="sentiment",
            stringValue="positive",
            timestamp="2025-01-01T00:00:00Z",
            source="ANNOTATION",
            dataType="CATEGORICAL",
        )
        assert score.string_value == "positive"
        assert score.source == "ANNOTATION"
        assert score.data_type == "CATEGORICAL"

    def test_score_with_observation(self):
        score = LangfuseScore(
            id="score-123",
            traceId="trace-456",
            observationId="obs-789",
            name="quality",
            value=4.5,
            timestamp="2025-01-01T00:00:00Z",
            source="EVAL",
            dataType="NUMERIC",
            comment="Great response!",
        )
        assert score.observation_id == "obs-789"
        assert score.comment == "Great response!"


class TestLangfuseResponses:
    """Tests for Langfuse response models."""

    def test_traces_response(self):
        resp = LangfuseTracesResponse(
            data=[
                LangfuseTrace(id="t1", timestamp="2025-01-01T00:00:00Z"),
                LangfuseTrace(id="t2", timestamp="2025-01-01T00:01:00Z"),
            ],
            meta={"page": 1, "limit": 50, "totalItems": 2},
        )
        assert len(resp.data) == 2
        assert resp.meta["totalItems"] == 2

    def test_sessions_response(self):
        resp = LangfuseSessionsResponse(
            data=[
                LangfuseSession(id="s1", createdAt="2025-01-01T00:00:00Z", projectId="p1"),
            ],
            meta={"page": 1},
        )
        assert len(resp.data) == 1

    def test_observations_response(self):
        resp = LangfuseObservationsResponse(
            data=[
                LangfuseObservation(
                    id="o1", traceId="t1", type="GENERATION", startTime="2025-01-01T00:00:00Z"
                ),
            ],
            meta={},
        )
        assert len(resp.data) == 1

    def test_scores_response(self):
        resp = LangfuseScoresResponse(
            data=[
                LangfuseScore(
                    id="sc1",
                    traceId="t1",
                    name="test",
                    timestamp="2025-01-01T00:00:00Z",
                    source="API",
                    dataType="NUMERIC",
                ),
            ],
            meta={},
        )
        assert len(resp.data) == 1


# ============================================================================
# Helper Function Tests
# ============================================================================


class TestFormatLangfuseDuration:
    """Tests for format_langfuse_duration."""

    def test_none_latency(self):
        assert format_langfuse_duration(None) is None

    def test_milliseconds(self):
        # 0.5 seconds = 500ms
        assert format_langfuse_duration(0.5) == "500ms"

    def test_seconds(self):
        # 2.5 seconds
        assert format_langfuse_duration(2.5) == "2.5s"

    def test_minutes(self):
        # 90 seconds = 1.5 minutes
        assert format_langfuse_duration(90) == "1.5m"


class TestLangfuseTraceToDict:
    """Tests for langfuse_trace_to_dict."""

    def test_basic_trace(self):
        trace = LangfuseTrace(
            id="trace-123",
            timestamp="2025-01-01T00:00:00Z",
            name="my-trace",
            tags=["tag1", "tag2"],
            latency=1.5,
            totalCost=0.01,
        )
        result = langfuse_trace_to_dict(trace)

        assert result["id"] == "trace-123"
        assert result["name"] == "my-trace"
        assert result["tags"] == ["tag1", "tag2"]
        assert result["latency"] == 1.5
        assert result["latency_formatted"] == "1.5s"
        assert result["total_cost"] == 0.01

    def test_trace_with_observations(self):
        trace = LangfuseTrace(
            id="trace-123",
            timestamp="2025-01-01T00:00:00Z",
            observations=["obs-1", "obs-2"],
        )
        result = langfuse_trace_to_dict(trace)

        assert result["observation_count"] == 2


class TestLangfuseObservationToDict:
    """Tests for langfuse_observation_to_dict."""

    def test_basic_observation(self):
        obs = LangfuseObservation(
            id="obs-123",
            traceId="trace-456",
            type="GENERATION",
            name="chat",
            startTime="2025-01-01T00:00:00Z",
            endTime="2025-01-01T00:00:01Z",
            model="gpt-4o-mini",
            latency=1.0,
        )
        result = langfuse_observation_to_dict(obs)

        assert result["id"] == "obs-123"
        assert result["type"] == "GENERATION"
        assert result["name"] == "chat"
        assert result["model"] == "gpt-4o-mini"
        assert result["latency"] == 1.0
        assert result["latency_formatted"] == "1.0s"

    def test_observation_with_costs(self):
        obs = LangfuseObservation(
            id="obs-123",
            traceId="trace-456",
            type="GENERATION",
            startTime="2025-01-01T00:00:00Z",
            calculatedInputCost=0.001,
            calculatedOutputCost=0.002,
            calculatedTotalCost=0.003,
        )
        result = langfuse_observation_to_dict(obs)

        assert result["cost"]["input"] == 0.001
        assert result["cost"]["output"] == 0.002
        assert result["cost"]["total"] == 0.003

    def test_observation_with_usage(self):
        obs = LangfuseObservation(
            id="obs-123",
            traceId="trace-456",
            type="GENERATION",
            startTime="2025-01-01T00:00:00Z",
            usage={"input": 100, "output": 50},
        )
        result = langfuse_observation_to_dict(obs)

        assert result["usage"] == {"input": 100, "output": 50}


class TestLangfuseSessionToDict:
    """Tests for langfuse_session_to_dict."""

    def test_basic_session(self):
        session = LangfuseSession(
            id="session-123",
            createdAt="2025-01-01T00:00:00Z",
            projectId="project-456",
            countTraces=5,
            totalCost=0.25,
            totalTokens=5000,
            inputTokens=3000,
            outputTokens=2000,
        )
        result = langfuse_session_to_dict(session)

        assert result["id"] == "session-123"
        assert result["created_at"] == "2025-01-01T00:00:00Z"
        assert result["trace_count"] == 5
        assert result["total_cost"] == 0.25
        assert result["total_tokens"] == 5000


# ============================================================================
# Provider Client Tests
# ============================================================================


class TestLangfuseClientInit:
    """Tests for LangfuseClient initialization."""

    def test_missing_keys_raises_error(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(AuthenticationError) as exc_info:
                LangfuseClient()
            assert "LANGFUSE_PUBLIC_KEY" in str(exc_info.value)

    def test_missing_secret_key_raises_error(self):
        with patch.dict("os.environ", {"LANGFUSE_PUBLIC_KEY": "pk-test"}, clear=True):
            with pytest.raises(AuthenticationError) as exc_info:
                LangfuseClient()
            assert "LANGFUSE_SECRET_KEY" in str(exc_info.value)

    def test_init_with_env_vars(self):
        with patch.dict(
            "os.environ",
            {
                "LANGFUSE_PUBLIC_KEY": "pk-test",
                "LANGFUSE_SECRET_KEY": "sk-test",
            },
            clear=True,
        ):
            client = LangfuseClient()
            assert client.public_key == "pk-test"
            assert client.secret_key == "sk-test"
            assert client.host == "https://cloud.langfuse.com"
            client.close()

    def test_init_with_custom_host(self):
        with patch.dict(
            "os.environ",
            {
                "LANGFUSE_PUBLIC_KEY": "pk-test",
                "LANGFUSE_SECRET_KEY": "sk-test",
                "LANGFUSE_HOST": "https://custom.langfuse.com",
            },
        ):
            client = LangfuseClient()
            assert client.host == "https://custom.langfuse.com"
            client.close()

    def test_init_with_explicit_params(self):
        client = LangfuseClient(
            public_key="pk-explicit",
            secret_key="sk-explicit",
            host="https://my-langfuse.com/",
        )
        assert client.public_key == "pk-explicit"
        assert client.secret_key == "sk-explicit"
        assert client.host == "https://my-langfuse.com"  # trailing slash removed
        client.close()

    def test_provider_name(self):
        client = LangfuseClient(
            public_key="pk-test",
            secret_key="sk-test",
        )
        assert client.name == "langfuse"
        client.close()


class TestLangfuseClientParseTimestamp:
    """Tests for LangfuseClient._parse_timestamp."""

    def setup_method(self):
        self.client = LangfuseClient(
            public_key="pk-test",
            secret_key="sk-test",
        )

    def teardown_method(self):
        self.client.close()

    def test_none_timestamp(self):
        assert self.client._parse_timestamp(None) is None

    def test_iso_format_passthrough(self):
        ts = "2025-01-01T12:00:00Z"
        assert self.client._parse_timestamp(ts) == ts

    def test_date_only(self):
        result = self.client._parse_timestamp("2025-01-01")
        assert "2025-01-01" in result
        assert "T" in result

    def test_datetime_with_space(self):
        result = self.client._parse_timestamp("2025-01-01 12:30:45")
        assert "T" in result


class TestLangfuseClientErrorHandling:
    """Tests for LangfuseClient error handling."""

    def setup_method(self):
        self.client = LangfuseClient(
            public_key="pk-test",
            secret_key="sk-test",
        )

    def teardown_method(self):
        self.client.close()

    def test_401_raises_authentication_error(self):
        mock_response = Mock()
        mock_response.status_code = 401
        with pytest.raises(AuthenticationError):
            self.client._handle_error_response(mock_response)

    def test_404_raises_not_found_error(self):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Trace not found"}
        with pytest.raises(NotFoundError) as exc_info:
            self.client._handle_error_response(mock_response)
        assert "Trace not found" in str(exc_info.value)

    def test_429_raises_rate_limit_error(self):
        mock_response = Mock()
        mock_response.status_code = 429
        with pytest.raises(RateLimitError):
            self.client._handle_error_response(mock_response)

    def test_500_raises_provider_error(self):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal error"}
        with pytest.raises(ProviderError) as exc_info:
            self.client._handle_error_response(mock_response)
        assert "Internal error" in str(exc_info.value)

    def test_error_without_json(self):
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.json.side_effect = Exception("No JSON")
        with pytest.raises(ProviderError) as exc_info:
            self.client._handle_error_response(mock_response)
        assert "HTTP 503" in str(exc_info.value)


class TestLangfuseClientContextManager:
    """Tests for LangfuseClient context manager."""

    def test_context_manager(self):
        with LangfuseClient(
            public_key="pk-test",
            secret_key="sk-test",
        ) as client:
            assert client.name == "langfuse"
        # Client should be closed after exiting context


# ============================================================================
# API Method Tests (with mocked HTTP)
# ============================================================================


class TestLangfuseClientTracesAPI:
    """Tests for LangfuseClient traces API."""

    def setup_method(self):
        self.client = LangfuseClient(
            public_key="pk-test",
            secret_key="sk-test",
        )

    def teardown_method(self):
        self.client.close()

    @patch.object(LangfuseClient, "_get")
    def test_list_traces_basic(self, mock_get):
        mock_get.return_value = {
            "data": [
                {"id": "t1", "timestamp": "2025-01-01T00:00:00Z"},
                {"id": "t2", "timestamp": "2025-01-01T00:01:00Z"},
            ],
            "meta": {"page": 1, "limit": 50},
        }

        result = self.client.list_traces()

        assert len(result.data) == 2
        assert result.data[0].id == "t1"
        mock_get.assert_called_once()

    @patch.object(LangfuseClient, "_get")
    def test_list_traces_with_filters(self, mock_get):
        mock_get.return_value = {"data": [], "meta": {}}

        self.client.list_traces(
            limit=10,
            page=2,
            user_id="user-123",
            name="my-trace",
            session_id="session-456",
            tags=["tag1", "tag2"],
            from_timestamp="2025-01-01",
            to_timestamp="2025-01-31",
        )

        call_args = mock_get.call_args
        params = call_args[1]["params"] if "params" in call_args[1] else call_args[0][1]
        assert params["limit"] == 10
        assert params["page"] == 2
        assert params["userId"] == "user-123"

    @patch.object(LangfuseClient, "_get")
    def test_get_trace(self, mock_get):
        mock_get.return_value = {
            "id": "trace-123",
            "timestamp": "2025-01-01T00:00:00Z",
            "name": "my-trace",
            "observations": [],
        }

        result = self.client.get_trace("trace-123")

        assert result.id == "trace-123"
        assert result.name == "my-trace"


class TestLangfuseClientSessionsAPI:
    """Tests for LangfuseClient sessions API."""

    def setup_method(self):
        self.client = LangfuseClient(
            public_key="pk-test",
            secret_key="sk-test",
        )

    def teardown_method(self):
        self.client.close()

    @patch.object(LangfuseClient, "_get")
    def test_list_sessions(self, mock_get):
        mock_get.return_value = {
            "data": [
                {"id": "s1", "createdAt": "2025-01-01T00:00:00Z", "projectId": "p1"},
            ],
            "meta": {},
        }

        result = self.client.list_sessions()

        assert len(result.data) == 1
        assert result.data[0].id == "s1"

    @patch.object(LangfuseClient, "_get")
    def test_get_session(self, mock_get):
        mock_get.return_value = {
            "id": "session-123",
            "createdAt": "2025-01-01T00:00:00Z",
            "projectId": "project-456",
            "countTraces": 5,
        }

        result = self.client.get_session("session-123")

        assert result.id == "session-123"
        assert result.count_traces == 5


class TestLangfuseClientObservationsAPI:
    """Tests for LangfuseClient observations API."""

    def setup_method(self):
        self.client = LangfuseClient(
            public_key="pk-test",
            secret_key="sk-test",
        )

    def teardown_method(self):
        self.client.close()

    @patch.object(LangfuseClient, "_get")
    def test_list_observations(self, mock_get):
        mock_get.return_value = {
            "data": [
                {
                    "id": "o1",
                    "traceId": "t1",
                    "type": "GENERATION",
                    "startTime": "2025-01-01T00:00:00Z",
                },
            ],
            "meta": {},
        }

        result = self.client.list_observations(trace_id="t1")

        assert len(result.data) == 1
        assert result.data[0].type == "GENERATION"

    @patch.object(LangfuseClient, "_get")
    def test_list_observations_by_type(self, mock_get):
        mock_get.return_value = {"data": [], "meta": {}}

        self.client.list_observations(obs_type="GENERATION")

        call_args = mock_get.call_args
        params = call_args[1]["params"] if "params" in call_args[1] else call_args[0][1]
        assert params["type"] == "GENERATION"

    @patch.object(LangfuseClient, "_get")
    def test_get_observation(self, mock_get):
        mock_get.return_value = {
            "id": "obs-123",
            "traceId": "trace-456",
            "type": "GENERATION",
            "startTime": "2025-01-01T00:00:00Z",
            "model": "gpt-4o-mini",
        }

        result = self.client.get_observation("obs-123")

        assert result.id == "obs-123"
        assert result.model == "gpt-4o-mini"


class TestLangfuseClientScoresAPI:
    """Tests for LangfuseClient scores API."""

    def setup_method(self):
        self.client = LangfuseClient(
            public_key="pk-test",
            secret_key="sk-test",
        )

    def teardown_method(self):
        self.client.close()

    @patch.object(LangfuseClient, "_get")
    def test_list_scores(self, mock_get):
        mock_get.return_value = {
            "data": [
                {
                    "id": "sc1",
                    "traceId": "t1",
                    "name": "accuracy",
                    "value": 0.95,
                    "timestamp": "2025-01-01T00:00:00Z",
                    "source": "API",
                    "dataType": "NUMERIC",
                },
            ],
            "meta": {},
        }

        result = self.client.list_scores(trace_id="t1")

        assert len(result.data) == 1
        assert result.data[0].name == "accuracy"
        assert result.data[0].value == 0.95

    @patch.object(LangfuseClient, "_get")
    def test_get_score(self, mock_get):
        mock_get.return_value = {
            "id": "score-123",
            "traceId": "trace-456",
            "name": "quality",
            "value": 4.5,
            "timestamp": "2025-01-01T00:00:00Z",
            "source": "ANNOTATION",
            "dataType": "NUMERIC",
            "comment": "Good response",
        }

        result = self.client.get_score("score-123")

        assert result.id == "score-123"
        assert result.name == "quality"
        assert result.comment == "Good response"


# ============================================================================
# Search Helper Function Tests
# ============================================================================


class TestTraceMatchesQuery:
    """Tests for _trace_matches_query helper function."""

    def test_matches_trace_id(self):
        trace = LangfuseTrace(
            id="trace-abc123",
            timestamp="2025-01-01T00:00:00Z",
        )
        assert _trace_matches_query(trace, "abc123") is True
        assert _trace_matches_query(trace, "xyz") is False

    def test_matches_trace_name(self):
        trace = LangfuseTrace(
            id="trace-123",
            timestamp="2025-01-01T00:00:00Z",
            name="my-workflow-agent",
        )
        assert _trace_matches_query(trace, "workflow") is True
        assert _trace_matches_query(trace, "WORKFLOW") is True  # case insensitive
        assert _trace_matches_query(trace, "other") is False

    def test_matches_user_id(self):
        trace = LangfuseTrace(
            id="trace-123",
            timestamp="2025-01-01T00:00:00Z",
            userId="user-alice",
        )
        assert _trace_matches_query(trace, "alice") is True
        assert _trace_matches_query(trace, "bob") is False

    def test_matches_session_id(self):
        trace = LangfuseTrace(
            id="trace-123",
            timestamp="2025-01-01T00:00:00Z",
            sessionId="session-prod-001",
        )
        assert _trace_matches_query(trace, "prod") is True
        assert _trace_matches_query(trace, "dev") is False

    def test_matches_tags(self):
        trace = LangfuseTrace(
            id="trace-123",
            timestamp="2025-01-01T00:00:00Z",
            tags=["production", "important", "v2"],
        )
        assert _trace_matches_query(trace, "production") is True
        assert _trace_matches_query(trace, "IMPORTANT") is True  # case insensitive
        assert _trace_matches_query(trace, "staging") is False

    def test_matches_release(self):
        trace = LangfuseTrace(
            id="trace-123",
            timestamp="2025-01-01T00:00:00Z",
            release="v1.2.3-beta",
        )
        assert _trace_matches_query(trace, "v1.2") is True
        assert _trace_matches_query(trace, "beta") is True
        assert _trace_matches_query(trace, "alpha") is False

    def test_no_match_empty_trace(self):
        trace = LangfuseTrace(
            id="trace-123",
            timestamp="2025-01-01T00:00:00Z",
        )
        assert _trace_matches_query(trace, "something") is False


class TestSessionMatchesQuery:
    """Tests for _session_matches_query helper function."""

    def test_matches_session_id(self):
        session = LangfuseSession(
            id="session-abc123",
            createdAt="2025-01-01T00:00:00Z",
            projectId="project-456",
        )
        assert _session_matches_query(session, "abc123") is True
        assert _session_matches_query(session, "xyz") is False

    def test_matches_user_ids(self):
        session = LangfuseSession(
            id="session-123",
            createdAt="2025-01-01T00:00:00Z",
            projectId="project-456",
            userIds=["alice", "bob", "charlie"],
        )
        assert _session_matches_query(session, "alice") is True
        assert _session_matches_query(session, "BOB") is True  # case insensitive
        assert _session_matches_query(session, "dave") is False

    def test_no_match_empty_session(self):
        session = LangfuseSession(
            id="session-123",
            createdAt="2025-01-01T00:00:00Z",
            projectId="project-456",
        )
        assert _session_matches_query(session, "something") is False


# ============================================================================
# Search Handler Tests
# ============================================================================


class TestHandleLangfuseSearchTraces:
    """Tests for handle_langfuse_search_traces handler."""

    @pytest.fixture
    def sample_traces(self):
        """Create sample traces for testing."""
        return [
            LangfuseTrace(
                id="trace-1",
                timestamp="2025-01-01T00:00:00Z",
                name="agent-workflow",
                userId="alice",
                tags=["production"],
                latency=1.5,
                totalCost=0.05,
                release="v1.0",
            ),
            LangfuseTrace(
                id="trace-2",
                timestamp="2025-01-01T01:00:00Z",
                name="chat-completion",
                userId="bob",
                tags=["staging"],
                latency=2.5,
                totalCost=0.10,
                release="v2.0",
            ),
            LangfuseTrace(
                id="trace-3",
                timestamp="2025-01-01T02:00:00Z",
                name="agent-workflow",
                userId="alice",
                tags=["production"],
                latency=5.0,
                totalCost=0.20,
                release="v1.0",
            ),
        ]

    @pytest.fixture
    def mock_langfuse_client(self):
        """Create a mock LangfuseClient that doesn't require API keys."""
        with patch("shepherd_mcp.server.LangfuseClient") as mock_class:
            mock_instance = Mock()
            mock_class.return_value.__enter__ = Mock(return_value=mock_instance)
            mock_class.return_value.__exit__ = Mock(return_value=False)
            yield mock_instance

    @pytest.mark.asyncio
    async def test_search_with_text_query(self, mock_langfuse_client, sample_traces):
        mock_langfuse_client.list_traces.return_value = LangfuseTracesResponse(
            data=sample_traces,
            meta={"page": 1, "limit": 50},
        )

        result = await handle_langfuse_search_traces({"query": "agent"})

        assert len(result) == 1
        import json

        data = json.loads(result[0].text)
        assert data["total_matches"] == 2  # trace-1 and trace-3 match "agent"
        assert data["filters_applied"]["query"] == "agent"

    @pytest.mark.asyncio
    async def test_search_with_release_filter(self, mock_langfuse_client, sample_traces):
        mock_langfuse_client.list_traces.return_value = LangfuseTracesResponse(
            data=sample_traces,
            meta={},
        )

        result = await handle_langfuse_search_traces({"release": "v2"})

        import json

        data = json.loads(result[0].text)
        assert data["total_matches"] == 1  # only trace-2 has v2.0
        assert data["traces"][0]["name"] == "chat-completion"

    @pytest.mark.asyncio
    async def test_search_with_min_cost_filter(self, mock_langfuse_client, sample_traces):
        mock_langfuse_client.list_traces.return_value = LangfuseTracesResponse(
            data=sample_traces,
            meta={},
        )

        result = await handle_langfuse_search_traces({"min_cost": 0.10})

        import json

        data = json.loads(result[0].text)
        assert data["total_matches"] == 2  # trace-2 (0.10) and trace-3 (0.20)

    @pytest.mark.asyncio
    async def test_search_with_max_cost_filter(self, mock_langfuse_client, sample_traces):
        mock_langfuse_client.list_traces.return_value = LangfuseTracesResponse(
            data=sample_traces,
            meta={},
        )

        result = await handle_langfuse_search_traces({"max_cost": 0.08})

        import json

        data = json.loads(result[0].text)
        assert data["total_matches"] == 1  # only trace-1 (0.05)

    @pytest.mark.asyncio
    async def test_search_with_min_latency_filter(self, mock_langfuse_client, sample_traces):
        mock_langfuse_client.list_traces.return_value = LangfuseTracesResponse(
            data=sample_traces,
            meta={},
        )

        result = await handle_langfuse_search_traces({"min_latency": 3.0})

        import json

        data = json.loads(result[0].text)
        assert data["total_matches"] == 1  # only trace-3 (5.0s)

    @pytest.mark.asyncio
    async def test_search_with_max_latency_filter(self, mock_langfuse_client, sample_traces):
        mock_langfuse_client.list_traces.return_value = LangfuseTracesResponse(
            data=sample_traces,
            meta={},
        )

        result = await handle_langfuse_search_traces({"max_latency": 2.0})

        import json

        data = json.loads(result[0].text)
        assert data["total_matches"] == 1  # only trace-1 (1.5s)

    @pytest.mark.asyncio
    async def test_search_with_combined_filters(self, mock_langfuse_client, sample_traces):
        mock_langfuse_client.list_traces.return_value = LangfuseTracesResponse(
            data=sample_traces,
            meta={},
        )

        result = await handle_langfuse_search_traces(
            {
                "query": "agent",
                "min_cost": 0.10,
                "release": "v1",
            }
        )

        import json

        data = json.loads(result[0].text)
        assert data["total_matches"] == 1  # only trace-3 matches all criteria
        assert data["filters_applied"]["query"] == "agent"
        assert data["filters_applied"]["min_cost"] == 0.10
        assert data["filters_applied"]["release"] == "v1"

    @pytest.mark.asyncio
    async def test_search_passes_api_filters(self, mock_langfuse_client):
        mock_langfuse_client.list_traces.return_value = LangfuseTracesResponse(
            data=[],
            meta={},
        )

        await handle_langfuse_search_traces(
            {
                "name": "my-trace",
                "user_id": "alice",
                "session_id": "session-123",
                "tags": ["prod"],
                "from_timestamp": "2025-01-01",
                "to_timestamp": "2025-01-31",
                "limit": 25,
                "page": 2,
            }
        )

        mock_langfuse_client.list_traces.assert_called_once_with(
            limit=25,
            page=2,
            name="my-trace",
            user_id="alice",
            session_id="session-123",
            tags=["prod"],
            from_timestamp="2025-01-01",
            to_timestamp="2025-01-31",
        )


class TestHandleLangfuseSearchSessions:
    """Tests for handle_langfuse_search_sessions handler."""

    @pytest.fixture
    def sample_sessions(self):
        """Create sample sessions for testing."""
        return [
            LangfuseSession(
                id="session-1",
                createdAt="2025-01-01T00:00:00Z",
                projectId="project-1",
                userIds=["alice"],
                countTraces=5,
                totalCost=0.50,
            ),
            LangfuseSession(
                id="session-2",
                createdAt="2025-01-01T01:00:00Z",
                projectId="project-1",
                userIds=["bob", "charlie"],
                countTraces=10,
                totalCost=1.00,
            ),
            LangfuseSession(
                id="session-3",
                createdAt="2025-01-01T02:00:00Z",
                projectId="project-1",
                userIds=["alice", "dave"],
                countTraces=3,
                totalCost=0.20,
            ),
        ]

    @pytest.fixture
    def mock_langfuse_client(self):
        """Create a mock LangfuseClient that doesn't require API keys."""
        with patch("shepherd_mcp.server.LangfuseClient") as mock_class:
            mock_instance = Mock()
            mock_class.return_value.__enter__ = Mock(return_value=mock_instance)
            mock_class.return_value.__exit__ = Mock(return_value=False)
            yield mock_instance

    @pytest.mark.asyncio
    async def test_search_with_text_query(self, mock_langfuse_client, sample_sessions):
        mock_langfuse_client.list_sessions.return_value = LangfuseSessionsResponse(
            data=sample_sessions,
            meta={},
        )

        result = await handle_langfuse_search_sessions({"query": "session-1"})

        import json

        data = json.loads(result[0].text)
        assert data["total_matches"] == 1
        assert data["sessions"][0]["id"] == "session-1"

    @pytest.mark.asyncio
    async def test_search_with_user_id_filter(self, mock_langfuse_client, sample_sessions):
        mock_langfuse_client.list_sessions.return_value = LangfuseSessionsResponse(
            data=sample_sessions,
            meta={},
        )

        result = await handle_langfuse_search_sessions({"user_id": "alice"})

        import json

        data = json.loads(result[0].text)
        assert data["total_matches"] == 2  # session-1 and session-3 have alice

    @pytest.mark.asyncio
    async def test_search_with_min_traces_filter(self, mock_langfuse_client, sample_sessions):
        mock_langfuse_client.list_sessions.return_value = LangfuseSessionsResponse(
            data=sample_sessions,
            meta={},
        )

        result = await handle_langfuse_search_sessions({"min_traces": 5})

        import json

        data = json.loads(result[0].text)
        assert data["total_matches"] == 2  # session-1 (5) and session-2 (10)

    @pytest.mark.asyncio
    async def test_search_with_max_traces_filter(self, mock_langfuse_client, sample_sessions):
        mock_langfuse_client.list_sessions.return_value = LangfuseSessionsResponse(
            data=sample_sessions,
            meta={},
        )

        result = await handle_langfuse_search_sessions({"max_traces": 5})

        import json

        data = json.loads(result[0].text)
        assert data["total_matches"] == 2  # session-1 (5) and session-3 (3)

    @pytest.mark.asyncio
    async def test_search_with_min_cost_filter(self, mock_langfuse_client, sample_sessions):
        mock_langfuse_client.list_sessions.return_value = LangfuseSessionsResponse(
            data=sample_sessions,
            meta={},
        )

        result = await handle_langfuse_search_sessions({"min_cost": 0.50})

        import json

        data = json.loads(result[0].text)
        assert data["total_matches"] == 2  # session-1 (0.50) and session-2 (1.00)

    @pytest.mark.asyncio
    async def test_search_with_max_cost_filter(self, mock_langfuse_client, sample_sessions):
        mock_langfuse_client.list_sessions.return_value = LangfuseSessionsResponse(
            data=sample_sessions,
            meta={},
        )

        result = await handle_langfuse_search_sessions({"max_cost": 0.50})

        import json

        data = json.loads(result[0].text)
        assert data["total_matches"] == 2  # session-1 (0.50) and session-3 (0.20)

    @pytest.mark.asyncio
    async def test_search_with_combined_filters(self, mock_langfuse_client, sample_sessions):
        mock_langfuse_client.list_sessions.return_value = LangfuseSessionsResponse(
            data=sample_sessions,
            meta={},
        )

        result = await handle_langfuse_search_sessions(
            {
                "user_id": "alice",
                "min_traces": 4,
                "min_cost": 0.40,
            }
        )

        import json

        data = json.loads(result[0].text)
        assert data["total_matches"] == 1  # only session-1 matches all criteria
        assert data["filters_applied"]["user_id"] == "alice"
        assert data["filters_applied"]["min_traces"] == 4
        assert data["filters_applied"]["min_cost"] == 0.40

    @pytest.mark.asyncio
    async def test_search_passes_api_filters(self, mock_langfuse_client):
        mock_langfuse_client.list_sessions.return_value = LangfuseSessionsResponse(
            data=[],
            meta={},
        )

        await handle_langfuse_search_sessions(
            {
                "from_timestamp": "2025-01-01",
                "to_timestamp": "2025-01-31",
                "limit": 25,
                "page": 2,
            }
        )

        mock_langfuse_client.list_sessions.assert_called_once_with(
            limit=25,
            page=2,
            from_timestamp="2025-01-01",
            to_timestamp="2025-01-31",
        )

    @pytest.mark.asyncio
    async def test_search_no_filters_returns_all(self, mock_langfuse_client, sample_sessions):
        mock_langfuse_client.list_sessions.return_value = LangfuseSessionsResponse(
            data=sample_sessions,
            meta={},
        )

        result = await handle_langfuse_search_sessions({})

        import json

        data = json.loads(result[0].text)
        assert data["total_matches"] == 3
        assert data["filters_applied"] == {}
