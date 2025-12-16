"""AIOBS provider client for Shepherd MCP."""

from __future__ import annotations

import os
from datetime import datetime

import httpx

from shepherd_mcp.models.aiobs import (
    Event,
    FunctionEvent,
    Session,
    SessionsResponse,
)
from shepherd_mcp.providers.base import (
    AuthenticationError,
    BaseProvider,
    NotFoundError,
    ProviderError,
)

DEFAULT_ENDPOINT = "https://shepherd-api-48963996968.us-central1.run.app"


class AIOBSClient(BaseProvider):
    """Client for AIOBS API."""

    def __init__(self, api_key: str | None = None, endpoint: str | None = None) -> None:
        """Initialize the client.

        Args:
            api_key: AIOBS API key. If not provided, reads from AIOBS_API_KEY env var.
            endpoint: AIOBS API endpoint URL. If not provided, reads from AIOBS_ENDPOINT
                     env var or uses the default.
        """
        self.api_key = api_key or os.environ.get("AIOBS_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "No API key provided. Set AIOBS_API_KEY environment variable."
            )

        self.endpoint = (endpoint or os.environ.get("AIOBS_ENDPOINT", DEFAULT_ENDPOINT)).rstrip("/")
        self._client = httpx.Client(timeout=30.0)

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "aiobs"

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        if response.status_code == 401:
            try:
                detail = response.json().get("detail", "Authentication failed")
            except Exception:
                detail = "Authentication failed"
            raise AuthenticationError(detail)

        if response.status_code == 404:
            try:
                detail = response.json().get("detail", "Not found")
            except Exception:
                detail = "Not found"
            raise NotFoundError(detail)

        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", f"HTTP {response.status_code}")
            except Exception:
                detail = f"HTTP {response.status_code}"
            raise ProviderError(detail)

    def list_sessions(self) -> SessionsResponse:
        """List all sessions.

        Returns:
            SessionsResponse with all sessions and their events.
        """
        response = self._client.post(
            f"{self.endpoint}/v1/sessions",
            json={"api_key": self.api_key},
        )

        self._handle_error_response(response)
        return SessionsResponse(**response.json())

    def get_session(self, session_id: str) -> SessionsResponse:
        """Get a specific session with its trace tree.

        Args:
            session_id: The session ID to fetch.

        Returns:
            SessionsResponse with the session data.
        """
        response = self._client.post(
            f"{self.endpoint}/v1/sessions/{session_id}/tree",
            json={"api_key": self.api_key},
        )

        self._handle_error_response(response)
        return SessionsResponse(**response.json())

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> AIOBSClient:
        return self

    def __exit__(self, *args) -> None:
        self.close()


# ============================================================================
# Filtering utilities
# ============================================================================


def parse_date(date_str: str) -> float:
    """Parse a date string to Unix timestamp."""
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).timestamp()
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS")


def session_matches_query(session: Session, query: str) -> bool:
    """Check if a session matches the text query."""
    query_lower = query.lower()
    if query_lower in session.id.lower():
        return True
    if query_lower in session.name.lower():
        return True
    if any(query_lower in str(value).lower() for value in session.labels.values()):
        return True
    return any(query_lower in str(value).lower() for value in session.meta.values())


def session_matches_labels(session: Session, labels: dict[str, str]) -> bool:
    """Check if a session has all the specified labels."""
    for key, value in labels.items():
        if key not in session.labels:
            return False
        if session.labels[key] != value:
            return False
    return True


def session_has_provider(
    session: Session,
    events: list[Event],
    function_events: list[FunctionEvent],
    provider: str,
) -> bool:
    """Check if a session has events from the specified provider."""
    provider_lower = provider.lower()
    for event in events:
        if event.session_id == session.id and event.provider.lower() == provider_lower:
            return True
    for event in function_events:
        if event.session_id == session.id and event.provider.lower() == provider_lower:
            return True
    return False


def session_has_model(
    session: Session,
    events: list[Event],
    model: str,
) -> bool:
    """Check if a session has events using the specified model."""
    model_lower = model.lower()
    for event in events:
        if event.session_id != session.id:
            continue
        if event.request:
            event_model = event.request.get("model", "")
            if model_lower in str(event_model).lower():
                return True
    return False


def session_has_errors(
    session: Session,
    events: list[Event],
    function_events: list[FunctionEvent],
) -> bool:
    """Check if a session has any errors."""
    if any(event.session_id == session.id and event.error for event in events):
        return True
    return any(event.session_id == session.id and event.error for event in function_events)


def session_has_function(
    session: Session,
    function_events: list[FunctionEvent],
    function_name: str,
) -> bool:
    """Check if a session has calls to the specified function."""
    name_lower = function_name.lower()
    for event in function_events:
        if event.session_id != session.id:
            continue
        if event.name and name_lower in event.name.lower():
            return True
        if event.module and name_lower in event.module.lower():
            return True
    return False


def eval_is_failed(evaluation: dict) -> bool:
    """Check if an evaluation result indicates failure."""
    if not isinstance(evaluation, dict):
        return False
    if evaluation.get("passed") is False:
        return True
    if evaluation.get("result") is False:
        return True
    if str(evaluation.get("status", "")).lower() in ("failed", "fail", "error"):
        return True
    return evaluation.get("success") is False


def session_has_failed_evals(
    session: Session,
    events: list[Event],
    function_events: list[FunctionEvent],
) -> bool:
    """Check if a session has any failed evaluations."""
    for event in events:
        if event.session_id != session.id:
            continue
        for evaluation in event.evaluations:
            if eval_is_failed(evaluation):
                return True
    for event in function_events:
        if event.session_id != session.id:
            continue
        for evaluation in event.evaluations:
            if eval_is_failed(evaluation):
                return True
    return False


def filter_sessions(
    response: SessionsResponse,
    query: str | None = None,
    labels: dict[str, str] | None = None,
    provider: str | None = None,
    model: str | None = None,
    function: str | None = None,
    after: float | None = None,
    before: float | None = None,
    has_errors: bool = False,
    evals_failed: bool = False,
) -> SessionsResponse:
    """Filter sessions based on criteria."""
    filtered_sessions = []

    for session in response.sessions:
        # Text query filter
        if query and not session_matches_query(session, query):
            continue

        # Labels filter
        if labels and not session_matches_labels(session, labels):
            continue

        # Provider filter
        if provider and not session_has_provider(
            session, response.events, response.function_events, provider
        ):
            continue

        # Model filter
        if model and not session_has_model(session, response.events, model):
            continue

        # Function filter
        if function and not session_has_function(session, response.function_events, function):
            continue

        # Date range filters
        if after and session.started_at < after:
            continue
        if before and session.started_at > before:
            continue

        # Errors filter
        if has_errors and not session_has_errors(
            session, response.events, response.function_events
        ):
            continue

        # Failed evaluations filter
        if evals_failed and not session_has_failed_evals(
            session, response.events, response.function_events
        ):
            continue

        filtered_sessions.append(session)

    # Filter events to only include those from matching sessions
    session_ids = {s.id for s in filtered_sessions}
    filtered_events = [e for e in response.events if e.session_id in session_ids]
    filtered_function_events = [e for e in response.function_events if e.session_id in session_ids]

    return SessionsResponse(
        sessions=filtered_sessions,
        events=filtered_events,
        function_events=filtered_function_events,
        trace_tree=response.trace_tree,
        enh_prompt_traces=response.enh_prompt_traces,
        generated_at=response.generated_at,
        version=response.version,
    )
