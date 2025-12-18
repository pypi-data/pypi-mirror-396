"""Type definitions for Plott Analytics SDK."""

from typing import TypedDict, Optional, Literal, Any, Dict, List
from typing_extensions import NotRequired


class PlottConfig(TypedDict):
    """Configuration for the Plott Analytics client."""
    api_key: str
    base_url: NotRequired[str]  # default: https://api.plott.ai
    environment: NotRequired[Literal['production', 'staging', 'development', 'test']]
    batch_size: NotRequired[int]  # default: 10
    flush_interval: NotRequired[float]  # default: 1.0 seconds
    retry_attempts: NotRequired[int]  # default: 3
    retry_delay: NotRequired[float]  # default: 1.0 seconds
    debug: NotRequired[bool]  # default: False


class SDKMetadata(TypedDict):
    """SDK metadata included with requests."""
    sdk_version: str
    framework: str
    language: str
    runtime: str
    environment: str


class Context(TypedDict, total=False):
    """Context information that can be attached to events."""
    customer_id: str
    session_id: str
    conversation_id: str
    turn_id: str
    parent_turn_id: str
    message_id: str
    correlation_id: str
    user_id: str
    source: str
    environment: str
    version: str
    node_id: str
    token_count: int
    model: str
    confidence: float
    latency: float
    cost: float
    transition_type: Literal['automatic', 'manual', 'error']
    duration: float
    sdk_environment: str
    tool_call_id: str
    tool_status: str


class EventBatchRequest(TypedDict):
    """Request payload for batch event ingestion."""
    events: List[Dict[str, Any]]
    batch_id: str


class IngestionResponse(TypedDict):
    """Response from the event ingestion API."""
    received: int
    processed: int
    failed: int
    errors: NotRequired[List[str]]
    timestamp: str
    batch_id: str
