"""Event types and factory functions for Plott Analytics SDK."""

import json
from enum import Enum
from typing import TypedDict, Optional, Any, Dict, Literal, Union
from typing_extensions import NotRequired
import uuid
from datetime import datetime


class EventType(str, Enum):
    """Event types aligned with the backend schema."""
    MESSAGE = "MESSAGE"
    STATE_SNAPSHOT = "STATE_SNAPSHOT"
    UI = "UI"
    ERROR = "ERROR"
    RUN_EVENT = "RUN_EVENT"
    CHECKPOINT = "CHECKPOINT"
    TOOL = "TOOL"
    CUSTOM = "CUSTOM"
    LLM_CALL = "LLM_CALL"


class BaseEvent(TypedDict, total=False):
    """Base event interface that all events extend."""
    id: str
    type: str
    timestamp: str
    turn_id: str
    run_id: str
    session_id: str
    context: Dict[str, Any]


class MessageEvent(BaseEvent):
    """Event for tracking messages between user and assistant."""
    type: Literal["MESSAGE"]
    role: Literal["user", "assistant", "system"]
    content: str
    token_count: NotRequired[int]
    model: NotRequired[str]
    finish_reason: NotRequired[str]


class StateSnapshotEvent(BaseEvent):
    """Event for tracking state snapshots."""
    type: Literal["STATE_SNAPSHOT"]
    snapshot: Dict[str, Any]


class ErrorEvent(BaseEvent):
    """Event for tracking errors."""
    type: Literal["ERROR"]
    error: "ErrorDetails"
    severity: NotRequired[Literal["low", "medium", "high", "critical"]]


class ErrorDetails(TypedDict):
    """Error details structure."""
    name: str
    message: str
    stack: NotRequired[str]
    code: NotRequired[str]


class RunEvent(BaseEvent):
    """Event for tracking run lifecycle (start/end/resume)."""
    type: Literal["RUN_EVENT"]
    value: Literal["start", "end", "resume"]


class ToolEvent(BaseEvent):
    """Event for tracking tool executions."""
    type: Literal["TOOL"]
    tool_call_id: str
    tool_name: NotRequired[str]
    tool_status: Literal["started", "completed", "failed"]
    args: NotRequired[Union[Dict[str, Any], str]]
    result: NotRequired[str]
    error: NotRequired[str]


class LLMCallEvent(BaseEvent):
    """Event for tracking LLM calls with token usage and latency."""
    type: Literal["LLM_CALL"]
    model: str
    provider: NotRequired[str]
    input_tokens: int
    output_tokens: int
    latency_ms: int
    finish_reason: NotRequired[str]
    is_streaming: NotRequired[bool]
    first_token_latency_ms: NotRequired[int]


class CustomEvent(BaseEvent):
    """Event for tracking custom/arbitrary events."""
    type: Literal["CUSTOM"]
    value: Any


# Union type of all analytics events
AnalyticsEvent = Union[
    MessageEvent,
    StateSnapshotEvent,
    ErrorEvent,
    RunEvent,
    ToolEvent,
    LLMCallEvent,
    CustomEvent,
]


def _generate_id() -> str:
    """Generate a unique event ID."""
    return str(uuid.uuid4())


def _generate_timestamp() -> str:
    """Generate an ISO timestamp."""
    return datetime.utcnow().isoformat() + "Z"


def create_message_event(
    role: Literal["user", "assistant", "system"],
    content: str,
    *,
    run_id: Optional[str] = None,
    session_id: Optional[str] = None,
    turn_id: Optional[str] = None,
    token_count: Optional[int] = None,
    model: Optional[str] = None,
    finish_reason: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> MessageEvent:
    """Create a message event."""
    event: MessageEvent = {
        "type": EventType.MESSAGE.value,
        "role": role,
        "content": content,
    }
    if run_id is not None:
        event["runId"] = run_id
    if session_id is not None:
        event["sessionId"] = session_id
    if turn_id is not None:
        event["turnId"] = turn_id
    if token_count is not None:
        event["tokenCount"] = token_count
    if model is not None:
        event["model"] = model
    if finish_reason is not None:
        event["finishReason"] = finish_reason
    if context is not None:
        event["context"] = context
    return event


def create_state_snapshot_event(
    snapshot: Dict[str, Any],
    role: Literal["user", "assistant", "system"],
    *,
    run_id: Optional[str] = None,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> StateSnapshotEvent:
    """Create a state snapshot event."""
    # Ensure snapshot is a dict - parse if it's a JSON string
    parsed_snapshot = json.loads(snapshot) if isinstance(snapshot, str) else snapshot
    event: StateSnapshotEvent = {
        "type": EventType.STATE_SNAPSHOT.value,
        "role": role,
        "snapshot": parsed_snapshot,
    }
    if run_id is not None:
        event["runId"] = run_id
    if session_id is not None:
        event["sessionId"] = session_id
    if context is not None:
        event["context"] = context
    return event


def create_error_event(
    error: ErrorDetails,
    *,
    run_id: Optional[str] = None,
    session_id: Optional[str] = None,
    severity: Optional[Literal["low", "medium", "high", "critical"]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> ErrorEvent:
    """Create an error event."""
    event: ErrorEvent = {
        "type": EventType.ERROR.value,
        "error": error,
    }
    if run_id is not None:
        event["runId"] = run_id
    if session_id is not None:
        event["sessionId"] = session_id
    if severity is not None:
        event["severity"] = severity
    if context is not None:
        event["context"] = context
    return event


def create_run_event(
    value: Literal["start", "end", "resume"],
    *,
    run_id: Optional[str] = None,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> RunEvent:
    """Create a run event."""
    event: RunEvent = {
        "type": EventType.RUN_EVENT.value,
        "value": value,
    }
    if run_id is not None:
        event["runId"] = run_id
    if session_id is not None:
        event["sessionId"] = session_id
    if context is not None:
        event["context"] = context
    return event


def create_tool_event(
    tool_call_id: str,
    tool_status: Literal["started", "completed", "failed"],
    *,
    tool_name: Optional[str] = None,
    args: Optional[Union[Dict[str, Any], str]] = None,
    result: Optional[str] = None,
    error: Optional[str] = None,
    run_id: Optional[str] = None,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> ToolEvent:
    """Create a tool event."""
    event: ToolEvent = {
        "type": EventType.TOOL.value,
        "toolCallId": tool_call_id,
        "toolStatus": tool_status,
    }
    if tool_name is not None:
        event["toolName"] = tool_name
    if args is not None:
        event["args"] = args
    if result is not None:
        event["result"] = result
    if error is not None:
        event["error"] = error
    if run_id is not None:
        event["runId"] = run_id
    if session_id is not None:
        event["sessionId"] = session_id
    if context is not None:
        event["context"] = context
    return event


def create_llm_call_event(
    model: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: int,
    *,
    provider: Optional[str] = None,
    finish_reason: Optional[str] = None,
    is_streaming: Optional[bool] = None,
    first_token_latency_ms: Optional[int] = None,
    run_id: Optional[str] = None,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> LLMCallEvent:
    """Create an LLM call event."""
    event: LLMCallEvent = {
        "type": EventType.LLM_CALL.value,
        "model": model,
        "inputTokens": input_tokens,
        "outputTokens": output_tokens,
        "latencyMs": latency_ms,
    }
    if provider is not None:
        event["provider"] = provider
    if finish_reason is not None:
        event["finishReason"] = finish_reason
    if is_streaming is not None:
        event["isStreaming"] = is_streaming
    if first_token_latency_ms is not None:
        event["firstTokenLatencyMs"] = first_token_latency_ms
    if run_id is not None:
        event["runId"] = run_id
    if session_id is not None:
        event["sessionId"] = session_id
    if context is not None:
        event["context"] = context
    return event


def create_custom_event(
    value: Any,
    *,
    run_id: Optional[str] = None,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> CustomEvent:
    """Create a custom event."""
    event: CustomEvent = {
        "type": EventType.CUSTOM.value,
        "value": value,
    }
    if run_id is not None:
        event["runId"] = run_id
    if session_id is not None:
        event["sessionId"] = session_id
    if context is not None:
        event["context"] = context
    return event
