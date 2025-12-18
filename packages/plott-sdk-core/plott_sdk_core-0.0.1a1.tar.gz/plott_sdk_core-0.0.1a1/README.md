# Plott SDK Core for Python

The core analytics client for Plott, providing event tracking with batching, retry logic, and async support.

## Installation

```bash
pip install plott-sdk-core
```

## Quick Start

```python
from plott_analytics import PlottAnalytics

# Initialize the client
client = PlottAnalytics({
    "api_key": "cpk_...",  # or set PLOTT_API_KEY env var
    "environment": "development",
})

# Track events
client.track_message_event(
    role="user",
    content="Hello, world!",
    run_id="run-123",
    session_id="session-456",
)

client.track_message_event(
    role="assistant",
    content="Hi there! How can I help you today?",
    run_id="run-123",
    session_id="session-456",
)

# Flush and shutdown when done
await client.flush()
await client.shutdown()
```

## Event Types

### Message Events
Track messages between users and AI assistants:

```python
client.track_message_event(
    role="user",  # or "assistant", "system"
    content="Message content",
    run_id="run-123",
    session_id="session-456",
    token_count=50,  # optional
    model="gpt-4",   # optional
)
```

### Run Events
Track the lifecycle of agent runs:

```python
client.track_run_event(value="start", run_id="run-123")
# ... agent execution ...
client.track_run_event(value="end", run_id="run-123")
```

### Tool Events
Track tool/function calls:

```python
client.track_tool_event(
    tool_call_id="call-123",
    tool_status="started",
    tool_name="search",
    args={"query": "latest news"},
)

client.track_tool_event(
    tool_call_id="call-123",
    tool_status="completed",
    result="Found 10 results...",
)
```

### State Snapshot Events
Track state changes:

```python
client.track_state_snapshot_event(
    snapshot={"messages": [...], "context": {...}},
    run_id="run-123",
)
```

### Error Events
Track errors:

```python
client.track_error_event(
    error={
        "name": "ValidationError",
        "message": "Invalid input",
        "code": "INVALID_INPUT",
    },
    run_id="run-123",
    severity="medium",
)
```

### LLM Call Events
Track LLM API calls with token usage:

```python
client.track_llm_call_event(
    model="gpt-4",
    input_tokens=100,
    output_tokens=50,
    latency_ms=1200,
    provider="openai",
    is_streaming=True,
)
```

## Configuration

```python
client = PlottAnalytics({
    "api_key": "cpk_...",           # Required
    "environment": "production",     # production, staging, development, test
    "retry_attempts": 3,             # Max retry attempts
    "retry_delay": 1.0,              # Initial retry delay (exponential backoff)
    "debug": False,                  # Enable debug logging
})
```

## License

MIT
