"""Plott Analytics SDK for Python."""

from .client import PlottAnalytics
from .types import PlottConfig, SDKMetadata, Context, EventBatchRequest, IngestionResponse
from .events import (
    EventType,
    BaseEvent,
    MessageEvent,
    StateSnapshotEvent,
    ErrorEvent,
    ErrorDetails,
    RunEvent,
    ToolEvent,
    LLMCallEvent,
    CustomEvent,
    AnalyticsEvent,
    create_message_event,
    create_state_snapshot_event,
    create_error_event,
    create_run_event,
    create_tool_event,
    create_llm_call_event,
    create_custom_event,
)

__all__ = [
    # Client
    "PlottAnalytics",
    # Types
    "PlottConfig",
    "SDKMetadata",
    "Context",
    "EventBatchRequest",
    "IngestionResponse",
    # Event types
    "EventType",
    "BaseEvent",
    "MessageEvent",
    "StateSnapshotEvent",
    "ErrorEvent",
    "ErrorDetails",
    "RunEvent",
    "ToolEvent",
    "LLMCallEvent",
    "CustomEvent",
    "AnalyticsEvent",
    # Factory functions
    "create_message_event",
    "create_state_snapshot_event",
    "create_error_event",
    "create_run_event",
    "create_tool_event",
    "create_llm_call_event",
    "create_custom_event",
]

__version__ = "0.1.0"
