"""Shepherd MCP Server - Debug your AI agents like you debug your code.

Supports multiple observability providers:
- AIOBS (Shepherd backend)
- Langfuse
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from shepherd_mcp.models.aiobs import (
    Event,
    FunctionEvent,
    SessionsResponse,
    TraceNode,
)
from shepherd_mcp.models.langfuse import (
    LangfuseObservation,
    LangfuseTrace,
)
from shepherd_mcp.providers.aiobs import (
    AIOBSClient,
    filter_sessions,
    parse_date,
)
from shepherd_mcp.providers.base import (
    AuthenticationError,
    NotFoundError,
    ProviderError,
    RateLimitError,
)
from shepherd_mcp.providers.langfuse import LangfuseClient

# Create the MCP server
server = Server("shepherd-mcp")


# ============================================================================
# Helper functions - AIOBS
# ============================================================================


def format_timestamp(ts: float) -> str:
    """Format a Unix timestamp to ISO format string."""
    return datetime.fromtimestamp(ts).isoformat()


def format_duration(ms: float) -> str:
    """Format duration in milliseconds to human-readable string."""
    if ms < 1000:
        return f"{ms:.0f}ms"
    elif ms < 60000:
        return f"{ms / 1000:.1f}s"
    else:
        return f"{ms / 60000:.1f}m"


def session_to_dict(
    session: Any, events: list[Event], function_events: list[FunctionEvent]
) -> dict:
    """Convert a session to a dictionary with computed fields."""
    # Count events for this session
    event_count = sum(1 for e in events if e.session_id == session.id)
    fn_event_count = sum(1 for e in function_events if e.session_id == session.id)

    # Calculate duration
    duration_ms = None
    if session.ended_at and session.started_at:
        duration_ms = (session.ended_at - session.started_at) * 1000

    return {
        "id": session.id,
        "name": session.name,
        "started_at": format_timestamp(session.started_at),
        "ended_at": format_timestamp(session.ended_at) if session.ended_at else None,
        "duration_ms": duration_ms,
        "duration": format_duration(duration_ms) if duration_ms else None,
        "llm_call_count": event_count,
        "function_call_count": fn_event_count,
        "total_event_count": event_count + fn_event_count,
        "labels": dict(session.labels),
        "meta": dict(session.meta),
    }


def calc_total_tokens(events: list[Event]) -> dict[str, int]:
    """Calculate total tokens from events."""
    total = {"input": 0, "output": 0, "total": 0}
    for event in events:
        if event.response and "usage" in event.response:
            usage = event.response["usage"]
            total["input"] += usage.get("prompt_tokens", 0) or usage.get("input_tokens", 0)
            total["output"] += usage.get("completion_tokens", 0) or usage.get("output_tokens", 0)
            total["total"] += usage.get("total_tokens", 0)
    return total


def calc_avg_latency(events: list[Event]) -> float:
    """Calculate average latency from events."""
    if not events:
        return 0.0
    return sum(e.duration_ms for e in events) / len(events)


def count_errors(events: list[Event], function_events: list[FunctionEvent]) -> int:
    """Count errors in events."""
    count = sum(1 for e in events if e.error)
    count += sum(1 for e in function_events if e.error)
    return count


def get_provider_distribution(events: list[Event]) -> dict[str, int]:
    """Get provider distribution from events."""
    dist: dict[str, int] = {}
    for event in events:
        dist[event.provider] = dist.get(event.provider, 0) + 1
    return dist


def get_model_distribution(events: list[Event]) -> dict[str, int]:
    """Get model distribution from events."""
    dist: dict[str, int] = {}
    for event in events:
        if event.request:
            model = event.request.get("model", "unknown")
            dist[model] = dist.get(model, 0) + 1
    return dist


def trace_node_to_dict(node: TraceNode) -> dict:
    """Convert a trace node to a simplified dictionary."""
    result = {
        "type": node.event_type or ("function" if node.name else "provider"),
        "provider": node.provider,
        "api": node.api,
        "duration_ms": node.duration_ms,
        "duration": format_duration(node.duration_ms),
        "span_id": node.span_id,
    }

    if node.name:
        result["function_name"] = node.name
        result["module"] = node.module

    if node.request and "model" in node.request:
        result["model"] = node.request["model"]

    if node.error:
        result["error"] = node.error

    if node.evaluations:
        result["evaluations"] = [
            {
                "type": e.get("eval_type"),
                "passed": e.get("passed"),
                "score": e.get("score"),
                "feedback": e.get("feedback"),
            }
            for e in node.evaluations
        ]

    if node.children:
        result["children"] = [trace_node_to_dict(child) for child in node.children]

    return result


# ============================================================================
# Helper functions - Langfuse
# ============================================================================


def format_langfuse_duration(latency: float | None) -> str | None:
    """Format latency in seconds to human-readable string."""
    if latency is None:
        return None
    ms = latency * 1000
    return format_duration(ms)


def langfuse_trace_to_dict(trace: LangfuseTrace) -> dict:
    """Convert a Langfuse trace to a dictionary."""
    return {
        "id": trace.id,
        "name": trace.name,
        "timestamp": trace.timestamp,
        "user_id": trace.user_id,
        "session_id": trace.session_id,
        "tags": trace.tags,
        "latency": trace.latency,
        "latency_formatted": format_langfuse_duration(trace.latency),
        "total_cost": trace.total_cost,
        "metadata": trace.metadata,
        "observation_count": len(trace.observations),
    }


def langfuse_observation_to_dict(obs: LangfuseObservation) -> dict:
    """Convert a Langfuse observation to a dictionary."""
    result: dict[str, Any] = {
        "id": obs.id,
        "type": obs.type,
        "name": obs.name,
        "start_time": obs.start_time,
        "end_time": obs.end_time,
        "model": obs.model,
        "latency": obs.latency,
        "latency_formatted": format_langfuse_duration(obs.latency),
        "level": obs.level,
    }

    if obs.usage:
        result["usage"] = obs.usage

    if obs.calculated_total_cost:
        result["cost"] = {
            "input": obs.calculated_input_cost,
            "output": obs.calculated_output_cost,
            "total": obs.calculated_total_cost,
        }

    if obs.status_message:
        result["status_message"] = obs.status_message

    if obs.parent_observation_id:
        result["parent_observation_id"] = obs.parent_observation_id

    return result


def langfuse_session_to_dict(session: Any) -> dict:
    """Convert a Langfuse session to a dictionary."""
    return {
        "id": session.id,
        "created_at": session.created_at,
        "trace_count": session.count_traces,
        "total_cost": session.total_cost,
        "total_tokens": session.total_tokens,
        "input_tokens": session.input_tokens,
        "output_tokens": session.output_tokens,
        "session_duration": session.session_duration,
        "user_ids": session.user_ids,
    }


# ============================================================================
# Diff calculation (AIOBS)
# ============================================================================


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


def count_evaluations(events: list[Event], function_events: list[FunctionEvent]) -> dict[str, int]:
    """Count evaluation results."""
    result = {"total": 0, "passed": 0, "failed": 0}
    all_evals = []
    for event in events:
        all_evals.extend(event.evaluations)
    for event in function_events:
        all_evals.extend(event.evaluations)

    result["total"] = len(all_evals)
    for ev in all_evals:
        if eval_is_failed(ev):
            result["failed"] += 1
        else:
            result["passed"] += 1
    return result


def get_trace_depth(nodes: list[TraceNode]) -> int:
    """Get maximum trace depth."""
    if not nodes:
        return 0

    def _depth(node: TraceNode) -> int:
        if not node.children:
            return 1
        return 1 + max(_depth(c) for c in node.children)

    return max(_depth(n) for n in nodes)


def get_errors_list(events: list[Event], function_events: list[FunctionEvent]) -> list[str]:
    """Get list of error messages."""
    errors = []
    for event in events:
        if event.error:
            errors.append(f"[{event.provider}/{event.api}] {event.error}")
    for event in function_events:
        if event.error:
            errors.append(f"[fn:{event.name}] {event.error}")
    return errors


def get_function_counts(function_events: list[FunctionEvent]) -> dict[str, int]:
    """Get function call counts."""
    counts: dict[str, int] = {}
    for event in function_events:
        if event.name:
            counts[event.name] = counts.get(event.name, 0) + 1
    return counts


def extract_system_prompts(events: list[Event]) -> list[dict]:
    """Extract system prompts from events."""
    prompts = []
    for i, event in enumerate(events):
        if not event.request:
            continue
        messages = event.request.get("messages", [])
        system_content = None

        # Check for system message in messages array
        for msg in messages:
            if isinstance(msg, dict) and msg.get("role") == "system":
                content = msg.get("content", "")
                if isinstance(content, list):
                    # Handle content blocks (e.g., Anthropic format)
                    content = " ".join(
                        block.get("text", "") for block in content if isinstance(block, dict)
                    )
                system_content = content
                break

        # Check for top-level system parameter (Anthropic style)
        if not system_content:
            system_content = event.request.get("system", "")

        if system_content:
            prompts.append(
                {
                    "index": i,
                    "provider": event.provider,
                    "model": event.request.get("model", "unknown"),
                    "content": system_content[:500] + "..."
                    if len(system_content) > 500
                    else system_content,
                    "full_length": len(system_content),
                }
            )
    return prompts


def compare_system_prompts(prompts1: list[dict], prompts2: list[dict]) -> dict:
    """Compare system prompts between sessions."""
    # Get unique prompts by content
    set1 = {p["content"] for p in prompts1}
    set2 = {p["content"] for p in prompts2}

    return {
        "session1": prompts1,
        "session2": prompts2,
        "unique_to_session1": list(set1 - set2),
        "unique_to_session2": list(set2 - set1),
        "common": list(set1 & set2),
        "changed": len(set1) != len(set2) or set1 != set2,
    }


def extract_request_params(events: list[Event]) -> list[dict]:
    """Extract request parameters from events."""
    params_list = []
    for i, event in enumerate(events):
        if not event.request:
            continue

        params = {
            "index": i,
            "provider": event.provider,
            "api": event.api,
            "model": event.request.get("model", "unknown"),
        }

        # Common parameters across providers
        param_keys = [
            "temperature",
            "max_tokens",
            "top_p",
            "top_k",
            "frequency_penalty",
            "presence_penalty",
            "stop",
            "stream",
            "tools",
            "tool_choice",
            "response_format",
        ]

        for key in param_keys:
            if key in event.request:
                value = event.request[key]
                # Summarize tools if present
                if key == "tools" and isinstance(value, list):
                    params[key] = [
                        t.get("function", {}).get("name", "unknown")
                        if isinstance(t, dict)
                        else str(t)
                        for t in value
                    ]
                else:
                    params[key] = value

        # Extract user message preview
        messages = event.request.get("messages", [])
        user_msgs = [m for m in messages if isinstance(m, dict) and m.get("role") == "user"]
        if user_msgs:
            last_user = user_msgs[-1]
            content = last_user.get("content", "")
            if isinstance(content, list):
                content = " ".join(
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                )
            params["user_message_preview"] = (
                content[:200] + "..." if len(str(content)) > 200 else content
            )

        params_list.append(params)
    return params_list


def compare_request_params(params1: list[dict], params2: list[dict]) -> dict:
    """Compare request parameters between sessions."""

    def aggregate_params(params_list: list[dict]) -> dict:
        agg: dict = {
            "temperatures": [],
            "max_tokens": [],
            "models": [],
            "tools_used": set(),
            "stream_count": 0,
        }
        for p in params_list:
            if "temperature" in p:
                agg["temperatures"].append(p["temperature"])
            if "max_tokens" in p:
                agg["max_tokens"].append(p["max_tokens"])
            agg["models"].append(p.get("model", "unknown"))
            if "tools" in p:
                agg["tools_used"].update(p["tools"])
            if p.get("stream"):
                agg["stream_count"] += 1
        agg["tools_used"] = list(agg["tools_used"])
        return agg

    agg1 = aggregate_params(params1)
    agg2 = aggregate_params(params2)

    return {
        "session1": {
            "requests": params1,
            "summary": {
                "avg_temperature": sum(agg1["temperatures"]) / len(agg1["temperatures"])
                if agg1["temperatures"]
                else None,
                "avg_max_tokens": sum(agg1["max_tokens"]) / len(agg1["max_tokens"])
                if agg1["max_tokens"]
                else None,
                "tools_used": agg1["tools_used"],
                "streaming_requests": agg1["stream_count"],
            },
        },
        "session2": {
            "requests": params2,
            "summary": {
                "avg_temperature": sum(agg2["temperatures"]) / len(agg2["temperatures"])
                if agg2["temperatures"]
                else None,
                "avg_max_tokens": sum(agg2["max_tokens"]) / len(agg2["max_tokens"])
                if agg2["max_tokens"]
                else None,
                "tools_used": agg2["tools_used"],
                "streaming_requests": agg2["stream_count"],
            },
        },
        "tools_added": list(set(agg2["tools_used"]) - set(agg1["tools_used"])),
        "tools_removed": list(set(agg1["tools_used"]) - set(agg2["tools_used"])),
    }


def extract_responses(events: list[Event]) -> list[dict]:
    """Extract response content from events."""
    responses = []
    for i, event in enumerate(events):
        if not event.response:
            continue

        model = event.response.get("model")
        if not model and event.request:
            model = event.request.get("model", "unknown")
        resp = {
            "index": i,
            "provider": event.provider,
            "model": model or "unknown",
            "duration_ms": event.duration_ms,
        }

        # Extract usage info
        usage = event.response.get("usage", {})
        if usage:
            resp["tokens"] = {
                "input": usage.get("prompt_tokens") or usage.get("input_tokens", 0),
                "output": usage.get("completion_tokens") or usage.get("output_tokens", 0),
                "total": usage.get("total_tokens", 0),
            }

        # Extract response content - handle different formats
        content = None

        # OpenAI format
        choices = event.response.get("choices", [])
        if choices and isinstance(choices, list):
            first_choice = choices[0]
            if isinstance(first_choice, dict):
                message = first_choice.get("message", {})
                content = message.get("content", "")
                # Check for tool calls
                tool_calls = message.get("tool_calls", [])
                if tool_calls:
                    resp["tool_calls"] = [
                        {
                            "name": tc.get("function", {}).get("name", "unknown"),
                            "arguments_preview": str(tc.get("function", {}).get("arguments", ""))[
                                :100
                            ],
                        }
                        for tc in tool_calls
                        if isinstance(tc, dict)
                    ]

        # Anthropic format
        if not content:
            content_blocks = event.response.get("content", [])
            if isinstance(content_blocks, list):
                text_blocks = [
                    b.get("text", "")
                    for b in content_blocks
                    if isinstance(b, dict) and b.get("type") == "text"
                ]
                content = " ".join(text_blocks)
                # Check for tool use
                tool_uses = [
                    b for b in content_blocks if isinstance(b, dict) and b.get("type") == "tool_use"
                ]
                if tool_uses:
                    resp["tool_calls"] = [
                        {
                            "name": tu.get("name", "unknown"),
                            "arguments_preview": str(tu.get("input", ""))[:100],
                        }
                        for tu in tool_uses
                    ]
            elif isinstance(content_blocks, str):
                content = content_blocks

        # Direct text field
        if not content:
            content = event.response.get("text", "")

        if content:
            resp["content_preview"] = content[:300] + "..." if len(str(content)) > 300 else content
            resp["content_length"] = len(str(content))

        # Stop reason
        stop_reason = event.response.get("stop_reason") or (
            choices[0].get("finish_reason") if choices else None
        )
        if stop_reason:
            resp["stop_reason"] = stop_reason

        responses.append(resp)
    return responses


def compare_responses(responses1: list[dict], responses2: list[dict]) -> dict:
    """Compare responses between sessions."""

    def summarize_responses(resp_list: list[dict]) -> dict:
        total_content_len = 0
        tool_call_count = 0
        stop_reasons: dict[str, int] = {}

        for r in resp_list:
            total_content_len += r.get("content_length", 0)
            tool_call_count += len(r.get("tool_calls", []))
            reason = r.get("stop_reason", "unknown")
            stop_reasons[reason] = stop_reasons.get(reason, 0) + 1

        return {
            "total_content_length": total_content_len,
            "avg_content_length": total_content_len / len(resp_list) if resp_list else 0,
            "tool_call_count": tool_call_count,
            "stop_reasons": stop_reasons,
        }

    summary1 = summarize_responses(responses1)
    summary2 = summarize_responses(responses2)

    return {
        "session1": {
            "responses": responses1,
            "summary": summary1,
        },
        "session2": {
            "responses": responses2,
            "summary": summary2,
        },
        "delta": {
            "avg_content_length": (summary2["avg_content_length"] - summary1["avg_content_length"]),
            "tool_call_count": (summary2["tool_call_count"] - summary1["tool_call_count"]),
        },
    }


def compute_session_diff(session1: SessionsResponse, session2: SessionsResponse) -> dict:
    """Compute the diff between two sessions."""
    s1 = session1.sessions[0] if session1.sessions else None
    s2 = session2.sessions[0] if session2.sessions else None

    if not s1 or not s2:
        return {"error": "One or both sessions not found"}

    # Session metadata
    s1_duration = (s1.ended_at - s1.started_at) * 1000 if s1.ended_at and s1.started_at else 0
    s2_duration = (s2.ended_at - s2.started_at) * 1000 if s2.ended_at and s2.started_at else 0

    # Labels diff
    s1_labels = set(s1.labels.items())
    s2_labels = set(s2.labels.items())
    labels_added = dict(s2_labels - s1_labels)
    labels_removed = dict(s1_labels - s2_labels)

    # Token calculations
    tokens1 = calc_total_tokens(session1.events)
    tokens2 = calc_total_tokens(session2.events)

    # Latency
    avg_latency1 = calc_avg_latency(session1.events)
    avg_latency2 = calc_avg_latency(session2.events)

    # Errors
    errors1 = count_errors(session1.events, session1.function_events)
    errors2 = count_errors(session2.events, session2.function_events)

    # Provider/model distribution
    providers1 = get_provider_distribution(session1.events)
    providers2 = get_provider_distribution(session2.events)
    models1 = get_model_distribution(session1.events)
    models2 = get_model_distribution(session2.events)

    # Function events
    fn_counts1 = get_function_counts(session1.function_events)
    fn_counts2 = get_function_counts(session2.function_events)
    fns1 = set(fn_counts1.keys())
    fns2 = set(fn_counts2.keys())

    # Evaluations
    evals1 = count_evaluations(session1.events, session1.function_events)
    evals2 = count_evaluations(session2.events, session2.function_events)

    # Trace depth
    trace_depth1 = get_trace_depth(session1.trace_tree)
    trace_depth2 = get_trace_depth(session2.trace_tree)

    # Errors list
    errors_list1 = get_errors_list(session1.events, session1.function_events)
    errors_list2 = get_errors_list(session2.events, session2.function_events)

    # System prompts comparison
    system_prompts1 = extract_system_prompts(session1.events)
    system_prompts2 = extract_system_prompts(session2.events)
    system_prompts_comparison = compare_system_prompts(system_prompts1, system_prompts2)

    # Request parameters comparison
    request_params1 = extract_request_params(session1.events)
    request_params2 = extract_request_params(session2.events)
    request_params_comparison = compare_request_params(request_params1, request_params2)

    # Responses comparison
    responses1 = extract_responses(session1.events)
    responses2 = extract_responses(session2.events)
    responses_comparison = compare_responses(responses1, responses2)

    return {
        "metadata": {
            "session1": {
                "id": s1.id,
                "name": s1.name,
                "started_at": format_timestamp(s1.started_at),
                "duration_ms": s1_duration,
                "duration": format_duration(s1_duration),
            },
            "session2": {
                "id": s2.id,
                "name": s2.name,
                "started_at": format_timestamp(s2.started_at),
                "duration_ms": s2_duration,
                "duration": format_duration(s2_duration),
            },
            "duration_delta_ms": s2_duration - s1_duration,
            "labels_added": labels_added,
            "labels_removed": labels_removed,
        },
        "llm_calls": {
            "session1": {
                "total": len(session1.events),
                "tokens": tokens1,
                "avg_latency_ms": round(avg_latency1, 2),
                "errors": errors1,
            },
            "session2": {
                "total": len(session2.events),
                "tokens": tokens2,
                "avg_latency_ms": round(avg_latency2, 2),
                "errors": errors2,
            },
            "delta": {
                "total": len(session2.events) - len(session1.events),
                "tokens": {
                    "input": tokens2["input"] - tokens1["input"],
                    "output": tokens2["output"] - tokens1["output"],
                    "total": tokens2["total"] - tokens1["total"],
                },
                "avg_latency_ms": round(avg_latency2 - avg_latency1, 2),
                "errors": errors2 - errors1,
            },
        },
        "providers": {"session1": providers1, "session2": providers2},
        "models": {"session1": models1, "session2": models2},
        "functions": {
            "session1": {
                "total": len(session1.function_events),
                "unique": len(fns1),
                "counts": fn_counts1,
            },
            "session2": {
                "total": len(session2.function_events),
                "unique": len(fns2),
                "counts": fn_counts2,
            },
            "only_in_session1": list(fns1 - fns2),
            "only_in_session2": list(fns2 - fns1),
            "in_both": list(fns1 & fns2),
        },
        "trace": {
            "session1": {"depth": trace_depth1, "root_nodes": len(session1.trace_tree)},
            "session2": {"depth": trace_depth2, "root_nodes": len(session2.trace_tree)},
        },
        "evaluations": {
            "session1": evals1,
            "session2": evals2,
            "delta": {
                "total": evals2["total"] - evals1["total"],
                "passed": evals2["passed"] - evals1["passed"],
                "failed": evals2["failed"] - evals1["failed"],
            },
            "pass_rate1": evals1["passed"] / evals1["total"] if evals1["total"] > 0 else 0,
            "pass_rate2": evals2["passed"] / evals2["total"] if evals2["total"] > 0 else 0,
        },
        "errors": {"session1": errors_list1, "session2": errors_list2},
        "system_prompts": system_prompts_comparison,
        "request_params": request_params_comparison,
        "responses": responses_comparison,
    }


# ============================================================================
# MCP Tool Handlers
# ============================================================================


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        # ====================================================================
        # AIOBS Tools
        # ====================================================================
        Tool(
            name="aiobs_list_sessions",
            description="[AIOBS] List all AI agent sessions from Shepherd. Returns session metadata, labels, and event counts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of sessions to return",
                    },
                },
            },
        ),
        Tool(
            name="aiobs_get_session",
            description="[AIOBS] Get detailed information about a specific AI agent session including the full trace tree, LLM calls, function events, and evaluations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The UUID of the session to retrieve",
                    },
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="aiobs_search_sessions",
            description="[AIOBS] Search and filter AI agent sessions with multiple criteria including text search, labels, provider, model, function name, date range, errors, and failed evaluations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text search query (matches session name, ID, labels, metadata)",
                    },
                    "labels": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                        "description": 'Filter by labels as key-value pairs (e.g., {"environment": "production"})',
                    },
                    "provider": {
                        "type": "string",
                        "description": "Filter by LLM provider (e.g., 'openai', 'anthropic')",
                    },
                    "model": {
                        "type": "string",
                        "description": "Filter by model name (e.g., 'gpt-4o-mini', 'claude-3')",
                    },
                    "function": {
                        "type": "string",
                        "description": "Filter by function name",
                    },
                    "after": {
                        "type": "string",
                        "description": "Sessions started after this date (YYYY-MM-DD or ISO format)",
                    },
                    "before": {
                        "type": "string",
                        "description": "Sessions started before this date (YYYY-MM-DD or ISO format)",
                    },
                    "has_errors": {
                        "type": "boolean",
                        "description": "Only return sessions that have errors",
                    },
                    "evals_failed": {
                        "type": "boolean",
                        "description": "Only return sessions with failed evaluations",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of sessions to return",
                    },
                },
            },
        ),
        Tool(
            name="aiobs_diff_sessions",
            description="[AIOBS] Compare two AI agent sessions and show their differences including metadata, LLM calls, tokens, latency, providers, models, functions, evaluations, errors, system prompts, request parameters, and response content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id_1": {
                        "type": "string",
                        "description": "First session UUID to compare",
                    },
                    "session_id_2": {
                        "type": "string",
                        "description": "Second session UUID to compare",
                    },
                },
                "required": ["session_id_1", "session_id_2"],
            },
        ),
        # ====================================================================
        # Langfuse Tools
        # ====================================================================
        Tool(
            name="langfuse_list_traces",
            description="[Langfuse] List traces with pagination and filters. Traces represent complete workflows or conversations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results per page (default: 50)",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number (1-indexed, default: 1)",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "Filter by user ID",
                    },
                    "name": {
                        "type": "string",
                        "description": "Filter by trace name",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Filter by session ID",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags",
                    },
                    "from_timestamp": {
                        "type": "string",
                        "description": "Filter traces starting after this timestamp (ISO format or YYYY-MM-DD)",
                    },
                    "to_timestamp": {
                        "type": "string",
                        "description": "Filter traces starting before this timestamp (ISO format or YYYY-MM-DD)",
                    },
                },
            },
        ),
        Tool(
            name="langfuse_get_trace",
            description="[Langfuse] Get a specific trace with its observations. Returns full trace data including all observations (generations, spans, events).",
            inputSchema={
                "type": "object",
                "properties": {
                    "trace_id": {
                        "type": "string",
                        "description": "The trace ID to fetch",
                    },
                },
                "required": ["trace_id"],
            },
        ),
        Tool(
            name="langfuse_list_sessions",
            description="[Langfuse] List sessions with pagination. Sessions group related traces together.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results per page (default: 50)",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number (1-indexed, default: 1)",
                    },
                    "from_timestamp": {
                        "type": "string",
                        "description": "Filter sessions created after this timestamp",
                    },
                    "to_timestamp": {
                        "type": "string",
                        "description": "Filter sessions created before this timestamp",
                    },
                },
            },
        ),
        Tool(
            name="langfuse_get_session",
            description="[Langfuse] Get a specific session with its metrics and aggregated data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID to fetch",
                    },
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="langfuse_list_observations",
            description="[Langfuse] List observations (generations, spans, events) with filters. Observations are the building blocks of traces.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results per page (default: 50)",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number (1-indexed, default: 1)",
                    },
                    "name": {
                        "type": "string",
                        "description": "Filter by observation name",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "Filter by user ID",
                    },
                    "trace_id": {
                        "type": "string",
                        "description": "Filter by trace ID",
                    },
                    "type": {
                        "type": "string",
                        "enum": ["GENERATION", "SPAN", "EVENT"],
                        "description": "Filter by observation type",
                    },
                    "from_timestamp": {
                        "type": "string",
                        "description": "Filter observations starting after this timestamp",
                    },
                    "to_timestamp": {
                        "type": "string",
                        "description": "Filter observations starting before this timestamp",
                    },
                },
            },
        ),
        Tool(
            name="langfuse_get_observation",
            description="[Langfuse] Get a specific observation with full details including input, output, usage, and costs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "observation_id": {
                        "type": "string",
                        "description": "The observation ID to fetch",
                    },
                },
                "required": ["observation_id"],
            },
        ),
        Tool(
            name="langfuse_list_scores",
            description="[Langfuse] List scores/evaluations with filters. Scores are attached to traces or observations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results per page (default: 50)",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number (1-indexed, default: 1)",
                    },
                    "name": {
                        "type": "string",
                        "description": "Filter by score name",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "Filter by user ID",
                    },
                    "trace_id": {
                        "type": "string",
                        "description": "Filter by trace ID",
                    },
                    "from_timestamp": {
                        "type": "string",
                        "description": "Filter scores created after this timestamp",
                    },
                    "to_timestamp": {
                        "type": "string",
                        "description": "Filter scores created before this timestamp",
                    },
                },
            },
        ),
        Tool(
            name="langfuse_get_score",
            description="[Langfuse] Get a specific score/evaluation with full details.",
            inputSchema={
                "type": "object",
                "properties": {
                    "score_id": {
                        "type": "string",
                        "description": "The score ID to fetch",
                    },
                },
                "required": ["score_id"],
            },
        ),
        Tool(
            name="langfuse_search_traces",
            description="[Langfuse] Search and filter traces with extended criteria including text search, release, cost range, and latency range. Combines API-level and client-side filtering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text search query (matches trace name, ID, user ID, session ID, or tags)",
                    },
                    "name": {
                        "type": "string",
                        "description": "Filter by trace name (API-level)",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "Filter by user ID",
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Filter by session ID",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags",
                    },
                    "release": {
                        "type": "string",
                        "description": "Filter by release (client-side)",
                    },
                    "min_cost": {
                        "type": "number",
                        "description": "Minimum total cost (client-side filter)",
                    },
                    "max_cost": {
                        "type": "number",
                        "description": "Maximum total cost (client-side filter)",
                    },
                    "min_latency": {
                        "type": "number",
                        "description": "Minimum latency in seconds (client-side filter)",
                    },
                    "max_latency": {
                        "type": "number",
                        "description": "Maximum latency in seconds (client-side filter)",
                    },
                    "from_timestamp": {
                        "type": "string",
                        "description": "Filter traces starting after this timestamp (ISO format or YYYY-MM-DD)",
                    },
                    "to_timestamp": {
                        "type": "string",
                        "description": "Filter traces starting before this timestamp (ISO format or YYYY-MM-DD)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 50)",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number (1-indexed, default: 1)",
                    },
                },
            },
        ),
        Tool(
            name="langfuse_search_sessions",
            description="[Langfuse] Search and filter sessions with extended criteria including text search, user ID, trace count range, and cost range. Combines API-level and client-side filtering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text search query (matches session ID or user IDs)",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "Filter by user ID (client-side)",
                    },
                    "min_traces": {
                        "type": "integer",
                        "description": "Minimum number of traces in session (client-side filter)",
                    },
                    "max_traces": {
                        "type": "integer",
                        "description": "Maximum number of traces in session (client-side filter)",
                    },
                    "min_cost": {
                        "type": "number",
                        "description": "Minimum total cost (client-side filter)",
                    },
                    "max_cost": {
                        "type": "number",
                        "description": "Maximum total cost (client-side filter)",
                    },
                    "from_timestamp": {
                        "type": "string",
                        "description": "Filter sessions created after this timestamp",
                    },
                    "to_timestamp": {
                        "type": "string",
                        "description": "Filter sessions created before this timestamp",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 50)",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number (1-indexed, default: 1)",
                    },
                },
            },
        ),
        # ====================================================================
        # Legacy aliases (for backwards compatibility)
        # ====================================================================
        Tool(
            name="list_sessions",
            description="[Deprecated: Use aiobs_list_sessions] List all AI agent sessions from Shepherd.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of sessions to return",
                    },
                },
            },
        ),
        Tool(
            name="get_session",
            description="[Deprecated: Use aiobs_get_session] Get detailed information about a specific AI agent session.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The UUID of the session to retrieve",
                    },
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="search_sessions",
            description="[Deprecated: Use aiobs_search_sessions] Search and filter AI agent sessions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "labels": {"type": "object", "additionalProperties": {"type": "string"}},
                    "provider": {"type": "string"},
                    "model": {"type": "string"},
                    "function": {"type": "string"},
                    "after": {"type": "string"},
                    "before": {"type": "string"},
                    "has_errors": {"type": "boolean"},
                    "evals_failed": {"type": "boolean"},
                    "limit": {"type": "integer"},
                },
            },
        ),
        Tool(
            name="diff_sessions",
            description="[Deprecated: Use aiobs_diff_sessions] Compare two AI agent sessions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id_1": {"type": "string"},
                    "session_id_2": {"type": "string"},
                },
                "required": ["session_id_1", "session_id_2"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        # AIOBS tools (with and without prefix)
        if name in ("aiobs_list_sessions", "list_sessions"):
            return await handle_aiobs_list_sessions(arguments)
        elif name in ("aiobs_get_session", "get_session"):
            return await handle_aiobs_get_session(arguments)
        elif name in ("aiobs_search_sessions", "search_sessions"):
            return await handle_aiobs_search_sessions(arguments)
        elif name in ("aiobs_diff_sessions", "diff_sessions"):
            return await handle_aiobs_diff_sessions(arguments)
        # Langfuse tools
        elif name == "langfuse_list_traces":
            return await handle_langfuse_list_traces(arguments)
        elif name == "langfuse_get_trace":
            return await handle_langfuse_get_trace(arguments)
        elif name == "langfuse_list_sessions":
            return await handle_langfuse_list_sessions(arguments)
        elif name == "langfuse_get_session":
            return await handle_langfuse_get_session(arguments)
        elif name == "langfuse_list_observations":
            return await handle_langfuse_list_observations(arguments)
        elif name == "langfuse_get_observation":
            return await handle_langfuse_get_observation(arguments)
        elif name == "langfuse_list_scores":
            return await handle_langfuse_list_scores(arguments)
        elif name == "langfuse_get_score":
            return await handle_langfuse_get_score(arguments)
        elif name == "langfuse_search_traces":
            return await handle_langfuse_search_traces(arguments)
        elif name == "langfuse_search_sessions":
            return await handle_langfuse_search_sessions(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except AuthenticationError as e:
        return [
            TextContent(
                type="text",
                text=f"Authentication error: {e}\n\nMake sure the required API keys are set in environment variables.",
            )
        ]
    except NotFoundError as e:
        return [TextContent(type="text", text=f"Not found: {e}")]
    except RateLimitError as e:
        return [TextContent(type="text", text=f"Rate limit exceeded: {e}")]
    except ProviderError as e:
        return [TextContent(type="text", text=f"API error: {e}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


# ============================================================================
# AIOBS Tool Handlers
# ============================================================================


async def handle_aiobs_list_sessions(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle aiobs_list_sessions tool call."""
    limit = arguments.get("limit")

    with AIOBSClient() as client:
        response = client.list_sessions()

    sessions = response.sessions
    if limit:
        sessions = sessions[:limit]

    result = {
        "provider": "aiobs",
        "sessions": [
            session_to_dict(s, response.events, response.function_events) for s in sessions
        ],
        "total": len(response.sessions),
        "returned": len(sessions),
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_aiobs_get_session(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle aiobs_get_session tool call."""
    session_id = arguments.get("session_id")
    if not session_id:
        return [TextContent(type="text", text="Error: session_id is required")]

    with AIOBSClient() as client:
        response = client.get_session(session_id)

    if not response.sessions:
        return [TextContent(type="text", text=f"Session not found: {session_id}")]

    session = response.sessions[0]

    # Build summary
    tokens = calc_total_tokens(response.events)
    providers = get_provider_distribution(response.events)
    models = get_model_distribution(response.events)
    evals = count_evaluations(response.events, response.function_events)
    errors = count_errors(response.events, response.function_events)

    result = {
        "provider": "aiobs",
        "session": session_to_dict(session, response.events, response.function_events),
        "summary": {
            "total_llm_calls": len(response.events),
            "total_function_calls": len(response.function_events),
            "total_tokens": tokens,
            "avg_latency_ms": round(calc_avg_latency(response.events), 2),
            "providers_used": list(providers.keys()),
            "models_used": list(models.keys()),
            "provider_distribution": providers,
            "model_distribution": models,
            "evaluations": evals,
            "errors": errors,
        },
        "trace_tree": [trace_node_to_dict(node) for node in response.trace_tree],
        "llm_calls": [
            {
                "provider": e.provider,
                "api": e.api,
                "model": e.request.get("model") if e.request else None,
                "duration_ms": e.duration_ms,
                "tokens": e.response.get("usage") if e.response else None,
                "error": e.error,
                "evaluations": [
                    {
                        "type": ev.get("eval_type"),
                        "passed": ev.get("passed"),
                        "score": ev.get("score"),
                    }
                    for ev in e.evaluations
                ],
            }
            for e in response.events[:50]  # Limit to first 50 for readability
        ],
        "function_calls": [
            {
                "name": e.name,
                "module": e.module,
                "duration_ms": e.duration_ms,
                "error": e.error,
            }
            for e in response.function_events[:50]  # Limit to first 50
        ],
    }

    # Add note if truncated
    if len(response.events) > 50:
        result["note"] = f"Showing first 50 of {len(response.events)} LLM calls"
    if len(response.function_events) > 50:
        result["note"] = (
            result.get("note", "") + f", first 50 of {len(response.function_events)} function calls"
        )

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_aiobs_search_sessions(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle aiobs_search_sessions tool call."""
    query = arguments.get("query")
    labels = arguments.get("labels")
    provider = arguments.get("provider")
    model = arguments.get("model")
    function = arguments.get("function")
    after_str = arguments.get("after")
    before_str = arguments.get("before")
    has_errors = arguments.get("has_errors", False)
    evals_failed = arguments.get("evals_failed", False)
    limit = arguments.get("limit")

    # Parse dates
    after = parse_date(after_str) if after_str else None
    before = parse_date(before_str) if before_str else None

    with AIOBSClient() as client:
        response = client.list_sessions()

    # Apply filters
    filtered = filter_sessions(
        response,
        query=query,
        labels=labels,
        provider=provider,
        model=model,
        function=function,
        after=after,
        before=before,
        has_errors=has_errors,
        evals_failed=evals_failed,
    )

    sessions = filtered.sessions
    if limit:
        sessions = sessions[:limit]

    # Build filters applied summary
    filters_applied = {}
    if query:
        filters_applied["query"] = query
    if labels:
        filters_applied["labels"] = labels
    if provider:
        filters_applied["provider"] = provider
    if model:
        filters_applied["model"] = model
    if function:
        filters_applied["function"] = function
    if after_str:
        filters_applied["after"] = after_str
    if before_str:
        filters_applied["before"] = before_str
    if has_errors:
        filters_applied["has_errors"] = True
    if evals_failed:
        filters_applied["evals_failed"] = True

    result = {
        "provider": "aiobs",
        "sessions": [
            session_to_dict(s, filtered.events, filtered.function_events) for s in sessions
        ],
        "total_matches": len(filtered.sessions),
        "returned": len(sessions),
        "filters_applied": filters_applied,
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_aiobs_diff_sessions(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle aiobs_diff_sessions tool call."""
    session_id_1 = arguments.get("session_id_1")
    session_id_2 = arguments.get("session_id_2")

    if not session_id_1 or not session_id_2:
        return [TextContent(type="text", text="Error: session_id_1 and session_id_2 are required")]

    with AIOBSClient() as client:
        session1 = client.get_session(session_id_1)
        session2 = client.get_session(session_id_2)

    if not session1.sessions:
        return [TextContent(type="text", text=f"Session not found: {session_id_1}")]
    if not session2.sessions:
        return [TextContent(type="text", text=f"Session not found: {session_id_2}")]

    diff = compute_session_diff(session1, session2)
    diff["provider"] = "aiobs"

    return [TextContent(type="text", text=json.dumps(diff, indent=2))]


# ============================================================================
# Langfuse Tool Handlers
# ============================================================================


async def handle_langfuse_list_traces(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle langfuse_list_traces tool call."""
    with LangfuseClient() as client:
        response = client.list_traces(
            limit=arguments.get("limit", 50),
            page=arguments.get("page", 1),
            user_id=arguments.get("user_id"),
            name=arguments.get("name"),
            session_id=arguments.get("session_id"),
            tags=arguments.get("tags"),
            from_timestamp=arguments.get("from_timestamp"),
            to_timestamp=arguments.get("to_timestamp"),
        )

    result = {
        "provider": "langfuse",
        "traces": [langfuse_trace_to_dict(t) for t in response.data],
        "meta": response.meta,
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_langfuse_get_trace(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle langfuse_get_trace tool call."""
    trace_id = arguments.get("trace_id")
    if not trace_id:
        return [TextContent(type="text", text="Error: trace_id is required")]

    with LangfuseClient() as client:
        trace = client.get_trace(trace_id)

    # Process observations
    observations = []
    for obs in trace.observations:
        if isinstance(obs, LangfuseObservation):
            observations.append(langfuse_observation_to_dict(obs))
        else:
            # Just an ID string
            observations.append({"id": obs})

    result = {
        "provider": "langfuse",
        "trace": langfuse_trace_to_dict(trace),
        "observations": observations,
        "input": trace.input,
        "output": trace.output,
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]


async def handle_langfuse_list_sessions(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle langfuse_list_sessions tool call."""
    with LangfuseClient() as client:
        response = client.list_sessions(
            limit=arguments.get("limit", 50),
            page=arguments.get("page", 1),
            from_timestamp=arguments.get("from_timestamp"),
            to_timestamp=arguments.get("to_timestamp"),
        )

    result = {
        "provider": "langfuse",
        "sessions": [langfuse_session_to_dict(s) for s in response.data],
        "meta": response.meta,
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_langfuse_get_session(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle langfuse_get_session tool call."""
    session_id = arguments.get("session_id")
    if not session_id:
        return [TextContent(type="text", text="Error: session_id is required")]

    with LangfuseClient() as client:
        session = client.get_session(session_id)

    result = {
        "provider": "langfuse",
        "session": langfuse_session_to_dict(session),
        "traces": [langfuse_trace_to_dict(t) for t in session.traces],
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_langfuse_list_observations(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle langfuse_list_observations tool call."""
    with LangfuseClient() as client:
        response = client.list_observations(
            limit=arguments.get("limit", 50),
            page=arguments.get("page", 1),
            name=arguments.get("name"),
            user_id=arguments.get("user_id"),
            trace_id=arguments.get("trace_id"),
            obs_type=arguments.get("type"),
            from_timestamp=arguments.get("from_timestamp"),
            to_timestamp=arguments.get("to_timestamp"),
        )

    result = {
        "provider": "langfuse",
        "observations": [langfuse_observation_to_dict(o) for o in response.data],
        "meta": response.meta,
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_langfuse_get_observation(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle langfuse_get_observation tool call."""
    observation_id = arguments.get("observation_id")
    if not observation_id:
        return [TextContent(type="text", text="Error: observation_id is required")]

    with LangfuseClient() as client:
        obs = client.get_observation(observation_id)

    result = {
        "provider": "langfuse",
        "observation": langfuse_observation_to_dict(obs),
        "input": obs.input,
        "output": obs.output,
        "model_parameters": obs.model_parameters,
        "metadata": obs.metadata,
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]


async def handle_langfuse_list_scores(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle langfuse_list_scores tool call."""
    with LangfuseClient() as client:
        response = client.list_scores(
            limit=arguments.get("limit", 50),
            page=arguments.get("page", 1),
            name=arguments.get("name"),
            user_id=arguments.get("user_id"),
            trace_id=arguments.get("trace_id"),
            from_timestamp=arguments.get("from_timestamp"),
            to_timestamp=arguments.get("to_timestamp"),
        )

    result = {
        "provider": "langfuse",
        "scores": [
            {
                "id": s.id,
                "name": s.name,
                "trace_id": s.trace_id,
                "observation_id": s.observation_id,
                "value": s.value,
                "string_value": s.string_value,
                "data_type": s.data_type,
                "source": s.source,
                "timestamp": s.timestamp,
                "comment": s.comment,
            }
            for s in response.data
        ],
        "meta": response.meta,
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_langfuse_get_score(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle langfuse_get_score tool call."""
    score_id = arguments.get("score_id")
    if not score_id:
        return [TextContent(type="text", text="Error: score_id is required")]

    with LangfuseClient() as client:
        score = client.get_score(score_id)

    result = {
        "provider": "langfuse",
        "score": {
            "id": score.id,
            "name": score.name,
            "trace_id": score.trace_id,
            "observation_id": score.observation_id,
            "value": score.value,
            "string_value": score.string_value,
            "data_type": score.data_type,
            "source": score.source,
            "timestamp": score.timestamp,
            "comment": score.comment,
            "config_id": score.config_id,
        },
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


# ============================================================================
# Langfuse Search Handlers
# ============================================================================


def _trace_matches_query(trace: LangfuseTrace, query: str) -> bool:
    """Check if a trace matches the text query."""
    query_lower = query.lower()
    # Match against trace ID
    if query_lower in trace.id.lower():
        return True
    # Match against trace name
    if trace.name and query_lower in trace.name.lower():
        return True
    # Match against user ID
    if trace.user_id and query_lower in trace.user_id.lower():
        return True
    # Match against session ID
    if trace.session_id and query_lower in trace.session_id.lower():
        return True
    # Match against tags
    for tag in trace.tags:
        if query_lower in tag.lower():
            return True
    # Match against release
    return bool(trace.release and query_lower in trace.release.lower())


def _session_matches_query(session: Any, query: str) -> bool:
    """Check if a session matches the text query."""
    query_lower = query.lower()
    # Match against session ID
    if query_lower in session.id.lower():
        return True
    # Match against user IDs
    return any(query_lower in user_id.lower() for user_id in session.user_ids)


async def handle_langfuse_search_traces(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle langfuse_search_traces tool call."""
    # Extract arguments
    query = arguments.get("query")
    name = arguments.get("name")
    user_id = arguments.get("user_id")
    session_id = arguments.get("session_id")
    tags = arguments.get("tags")
    release = arguments.get("release")
    min_cost = arguments.get("min_cost")
    max_cost = arguments.get("max_cost")
    min_latency = arguments.get("min_latency")
    max_latency = arguments.get("max_latency")
    from_timestamp = arguments.get("from_timestamp")
    to_timestamp = arguments.get("to_timestamp")
    limit = arguments.get("limit", 50)
    page = arguments.get("page", 1)

    with LangfuseClient() as client:
        # Use API-level filters where supported
        response = client.list_traces(
            limit=limit,
            page=page,
            name=name,
            user_id=user_id,
            session_id=session_id,
            tags=tags,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
        )

    # Apply additional client-side filters
    filtered_traces = response.data

    # Text query filter
    if query:
        filtered_traces = [t for t in filtered_traces if _trace_matches_query(t, query)]

    # Release filter (client-side)
    if release:
        release_lower = release.lower()
        filtered_traces = [
            t for t in filtered_traces if t.release and release_lower in t.release.lower()
        ]

    # Cost filters (client-side)
    if min_cost is not None:
        filtered_traces = [
            t for t in filtered_traces if t.total_cost is not None and t.total_cost >= min_cost
        ]
    if max_cost is not None:
        filtered_traces = [
            t for t in filtered_traces if t.total_cost is not None and t.total_cost <= max_cost
        ]

    # Latency filters (client-side)
    if min_latency is not None:
        filtered_traces = [
            t for t in filtered_traces if t.latency is not None and t.latency >= min_latency
        ]
    if max_latency is not None:
        filtered_traces = [
            t for t in filtered_traces if t.latency is not None and t.latency <= max_latency
        ]

    # Build filters applied summary
    filters_applied: dict[str, Any] = {}
    if query:
        filters_applied["query"] = query
    if name:
        filters_applied["name"] = name
    if user_id:
        filters_applied["user_id"] = user_id
    if session_id:
        filters_applied["session_id"] = session_id
    if tags:
        filters_applied["tags"] = tags
    if release:
        filters_applied["release"] = release
    if min_cost is not None:
        filters_applied["min_cost"] = min_cost
    if max_cost is not None:
        filters_applied["max_cost"] = max_cost
    if min_latency is not None:
        filters_applied["min_latency"] = min_latency
    if max_latency is not None:
        filters_applied["max_latency"] = max_latency
    if from_timestamp:
        filters_applied["from_timestamp"] = from_timestamp
    if to_timestamp:
        filters_applied["to_timestamp"] = to_timestamp

    result = {
        "provider": "langfuse",
        "traces": [langfuse_trace_to_dict(t) for t in filtered_traces],
        "total_matches": len(filtered_traces),
        "filters_applied": filters_applied,
        "meta": response.meta,
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_langfuse_search_sessions(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle langfuse_search_sessions tool call."""
    # Extract arguments
    query = arguments.get("query")
    user_id = arguments.get("user_id")
    min_traces = arguments.get("min_traces")
    max_traces = arguments.get("max_traces")
    min_cost = arguments.get("min_cost")
    max_cost = arguments.get("max_cost")
    from_timestamp = arguments.get("from_timestamp")
    to_timestamp = arguments.get("to_timestamp")
    limit = arguments.get("limit", 50)
    page = arguments.get("page", 1)

    with LangfuseClient() as client:
        response = client.list_sessions(
            limit=limit,
            page=page,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
        )

    # Apply client-side filters
    filtered_sessions = response.data

    # Text query filter
    if query:
        filtered_sessions = [s for s in filtered_sessions if _session_matches_query(s, query)]

    # User ID filter
    if user_id:
        user_id_lower = user_id.lower()
        filtered_sessions = [
            s for s in filtered_sessions if any(user_id_lower in uid.lower() for uid in s.user_ids)
        ]

    # Trace count filters
    if min_traces is not None:
        filtered_sessions = [s for s in filtered_sessions if s.count_traces >= min_traces]
    if max_traces is not None:
        filtered_sessions = [s for s in filtered_sessions if s.count_traces <= max_traces]

    # Cost filters
    if min_cost is not None:
        filtered_sessions = [s for s in filtered_sessions if s.total_cost >= min_cost]
    if max_cost is not None:
        filtered_sessions = [s for s in filtered_sessions if s.total_cost <= max_cost]

    # Build filters applied summary
    filters_applied: dict[str, Any] = {}
    if query:
        filters_applied["query"] = query
    if user_id:
        filters_applied["user_id"] = user_id
    if min_traces is not None:
        filters_applied["min_traces"] = min_traces
    if max_traces is not None:
        filters_applied["max_traces"] = max_traces
    if min_cost is not None:
        filters_applied["min_cost"] = min_cost
    if max_cost is not None:
        filters_applied["max_cost"] = max_cost
    if from_timestamp:
        filters_applied["from_timestamp"] = from_timestamp
    if to_timestamp:
        filters_applied["to_timestamp"] = to_timestamp

    result = {
        "provider": "langfuse",
        "sessions": [langfuse_session_to_dict(s) for s in filtered_sessions],
        "total_matches": len(filtered_sessions),
        "filters_applied": filters_applied,
        "meta": response.meta,
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


# ============================================================================
# Main entry point
# ============================================================================


def main():
    """Run the Shepherd MCP server."""
    import asyncio

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    asyncio.run(run())


if __name__ == "__main__":
    main()
