# 🐑 Shepherd MCP

MCP (Model Context Protocol) server for Shepherd - Debug your AI agents like you debug your code.

This MCP server allows AI assistants (Claude, Cursor, etc.) to query and analyze your AI agent sessions from multiple observability providers.

## Supported Providers

- **AIOBS** (Shepherd backend) - Native Shepherd observability
- **Langfuse** - Open-source LLM observability platform

## Installation

```bash
pip install shepherd-mcp
```

Or run directly with uvx:

```bash
uvx shepherd-mcp
```

## Configuration

### Environment Variables

#### AIOBS (Shepherd)

- `AIOBS_API_KEY` (required) - Your Shepherd API key
- `AIOBS_ENDPOINT` (optional) - Custom API endpoint URL

#### Langfuse

- `LANGFUSE_PUBLIC_KEY` (required) - Your Langfuse public API key
- `LANGFUSE_SECRET_KEY` (required) - Your Langfuse secret API key
- `LANGFUSE_HOST` (optional) - Custom Langfuse host URL (defaults to cloud.langfuse.com)

### .env File Support

shepherd-mcp automatically loads `.env` files from the current directory or any parent directory. This means if you have a `.env` file in your project root:

```bash
# .env
# AIOBS
AIOBS_API_KEY=aiobs_sk_xxxx

# Langfuse
LANGFUSE_PUBLIC_KEY=pk-lf-xxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

It will be automatically loaded when the MCP server starts.

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "shepherd": {
      "command": "uvx",
      "args": ["shepherd-mcp"],
      "env": {
        "AIOBS_API_KEY": "aiobs_sk_xxxx",
        "LANGFUSE_PUBLIC_KEY": "pk-lf-xxxx",
        "LANGFUSE_SECRET_KEY": "sk-lf-xxxx",
        "LANGFUSE_HOST": "https://cloud.langfuse.com"
      }
    }
  }
}
```

### Cursor

Add to your `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "shepherd": {
      "command": "uvx",
      "args": ["shepherd-mcp"],
      "env": {
        "AIOBS_API_KEY": "aiobs_sk_xxxx",
        "LANGFUSE_PUBLIC_KEY": "pk-lf-xxxx",
        "LANGFUSE_SECRET_KEY": "sk-lf-xxxx",
        "LANGFUSE_HOST": "https://cloud.langfuse.com"
      }
    }
  }
}
```

Or if installed via pip:

```json
{
  "mcpServers": {
    "shepherd": {
      "command": "shepherd-mcp",
      "env": {
        "AIOBS_API_KEY": "aiobs_sk_xxxx",
        "LANGFUSE_PUBLIC_KEY": "pk-lf-xxxx",
        "LANGFUSE_SECRET_KEY": "sk-lf-xxxx",
        "LANGFUSE_HOST": "https://cloud.langfuse.com"
      }
    }
  }
}
```

## Available Tools

### AIOBS (Shepherd) Tools

#### `aiobs_list_sessions`

List all AI agent sessions from Shepherd.

**Parameters:**
- `limit` (optional): Maximum number of sessions to return

**Example prompt:**
> "List my recent AI agent sessions from AIOBS"

#### `aiobs_get_session`

Get detailed information about a specific session including the full trace tree, LLM calls, function events, and evaluations.

**Parameters:**
- `session_id` (required): The UUID of the session to retrieve

**Example prompt:**
> "Get AIOBS session details for abc123-def456"

#### `aiobs_search_sessions`

Search and filter sessions with multiple criteria.

**Parameters:**
- `query` (optional): Text search (matches name, ID, labels, metadata)
- `labels` (optional): Filter by labels as key-value pairs
- `provider` (optional): Filter by LLM provider (e.g., 'openai', 'anthropic')
- `model` (optional): Filter by model name (e.g., 'gpt-4o-mini', 'claude-3')
- `function` (optional): Filter by function name
- `after` (optional): Sessions started after date (YYYY-MM-DD)
- `before` (optional): Sessions started before date (YYYY-MM-DD)
- `has_errors` (optional): Only return sessions with errors
- `evals_failed` (optional): Only return sessions with failed evaluations
- `limit` (optional): Maximum number of sessions to return

**Example prompts:**
> "Find all AIOBS sessions that used OpenAI with errors"
> "Search for sessions from yesterday that failed evaluations"

#### `aiobs_diff_sessions`

Compare two sessions and show their differences including:
- **Metadata**: Duration, labels, timestamps
- **LLM calls**: Count, tokens (input/output/total), average latency, errors
- **Provider/Model distribution**: Which providers and models were used
- **Function events**: Total calls, unique functions, function-specific counts
- **Trace structure**: Trace depth, root nodes
- **Evaluations**: Pass/fail counts and rates
- **System prompts**: Compare system prompts across sessions
- **Request parameters**: Temperature, max_tokens, tools used
- **Response content**: Content length, tool calls, stop reasons

**Parameters:**
- `session_id_1` (required): First session UUID to compare
- `session_id_2` (required): Second session UUID to compare

**Example prompt:**
> "Compare AIOBS sessions abc123 and def456"

---

### Langfuse Tools

#### `langfuse_list_traces`

List traces with pagination and filters. Traces represent complete workflows or conversations.

**Parameters:**
- `limit` (optional): Maximum results per page (default: 50)
- `page` (optional): Page number (1-indexed)
- `user_id` (optional): Filter by user ID
- `name` (optional): Filter by trace name
- `session_id` (optional): Filter by session ID
- `tags` (optional): Filter by tags
- `from_timestamp` (optional): Filter after timestamp
- `to_timestamp` (optional): Filter before timestamp

**Example prompt:**
> "List the last 20 Langfuse traces"

#### `langfuse_get_trace`

Get a specific trace with its observations (generations, spans, events).

**Parameters:**
- `trace_id` (required): The trace ID to fetch

**Example prompt:**
> "Get Langfuse trace details for trace-id-123"

#### `langfuse_list_sessions`

List sessions with pagination. Sessions group related traces together.

**Parameters:**
- `limit` (optional): Maximum results per page
- `page` (optional): Page number
- `from_timestamp` (optional): Filter after timestamp
- `to_timestamp` (optional): Filter before timestamp

**Example prompt:**
> "Show me Langfuse sessions from the last week"

#### `langfuse_get_session`

Get a specific session with its metrics and traces.

**Parameters:**
- `session_id` (required): The session ID to fetch

**Example prompt:**
> "Get Langfuse session details for session-123"

#### `langfuse_list_observations`

List observations (generations, spans, events) with filters.

**Parameters:**
- `limit` (optional): Maximum results per page
- `page` (optional): Page number
- `name` (optional): Filter by observation name
- `user_id` (optional): Filter by user ID
- `trace_id` (optional): Filter by trace ID
- `type` (optional): Filter by type (GENERATION, SPAN, EVENT)
- `from_timestamp` (optional): Filter after timestamp
- `to_timestamp` (optional): Filter before timestamp

**Example prompt:**
> "List all GENERATION type observations from Langfuse"

#### `langfuse_get_observation`

Get a specific observation with full details including input, output, usage, and costs.

**Parameters:**
- `observation_id` (required): The observation ID to fetch

**Example prompt:**
> "Get details for Langfuse observation obs-123"

#### `langfuse_list_scores`

List scores/evaluations with filters.

**Parameters:**
- `limit` (optional): Maximum results per page
- `page` (optional): Page number
- `name` (optional): Filter by score name
- `user_id` (optional): Filter by user ID
- `trace_id` (optional): Filter by trace ID
- `from_timestamp` (optional): Filter after timestamp
- `to_timestamp` (optional): Filter before timestamp

**Example prompt:**
> "Show me Langfuse scores for trace trace-123"

#### `langfuse_get_score`

Get a specific score/evaluation with full details.

**Parameters:**
- `score_id` (required): The score ID to fetch

**Example prompt:**
> "Get Langfuse score details for score-123"

---

### Legacy Tools (Deprecated)

For backwards compatibility, the following tools are still available but will be removed in a future version:

- `list_sessions` → Use `aiobs_list_sessions`
- `get_session` → Use `aiobs_get_session`
- `search_sessions` → Use `aiobs_search_sessions`
- `diff_sessions` → Use `aiobs_diff_sessions`

## Use Cases

### 1. Debugging Failed Runs

> "Show me all AIOBS sessions that had errors in the last 24 hours"

### 2. Performance Analysis

> "Compare AIOBS session abc123 with session def456 and tell me which one was more efficient"

### 3. Prompt Regression Detection

> "Find Langfuse traces with failed evaluations"

### 4. Cost Tracking

> "List Langfuse observations and summarize the total cost"

### 5. Session Inspection

> "Get the full trace tree for the most recent Langfuse trace and explain what happened"

### 6. Cross-Provider Analysis

> "Show me both AIOBS sessions and Langfuse traces from today"

## Development

### Setup

```bash
git clone https://github.com/neuralis/shepherd-mcp
cd shepherd-mcp
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Running Locally

```bash
export AIOBS_API_KEY=aiobs_sk_xxxx
export LANGFUSE_PUBLIC_KEY=pk-lf-xxxx
export LANGFUSE_SECRET_KEY=sk-lf-xxxx
python -m shepherd_mcp
```

### Publishing to PyPI

Releases are automatically published to PyPI via GitHub Actions when a release is created.

To publish manually:

```bash
# Build the package
pip install build twine
python -m build

# Upload to PyPI
twine upload dist/*
```

## Architecture

```
src/shepherd_mcp/
├── __init__.py          # Package exports
├── __main__.py          # Entry point
├── server.py            # MCP server with tool handlers
├── models/              # Data models
│   ├── __init__.py
│   ├── aiobs.py         # AIOBS-specific models
│   └── langfuse.py      # Langfuse-specific models
└── providers/           # Provider clients
    ├── __init__.py
    ├── base.py          # Base provider interface
    ├── aiobs.py         # AIOBS client implementation
    └── langfuse.py      # Langfuse client implementation
```

```
┌─────────────────┐     stdio      ┌─────────────────┐
│  Cursor/Claude  │ ◄────────────► │  shepherd-mcp   │
│    (Client)     │   stdin/stdout │   (subprocess)  │
└─────────────────┘                └────────┬────────┘
                                            │ HTTPS
                                  ┌─────────┴─────────┐
                                  │                   │
                                  ▼                   ▼
                         ┌─────────────┐     ┌─────────────┐
                         │ Shepherd API│     │ Langfuse API│
                         │   (AIOBS)   │     │   (Cloud)   │
                         └─────────────┘     └─────────────┘
```

## License

MIT
