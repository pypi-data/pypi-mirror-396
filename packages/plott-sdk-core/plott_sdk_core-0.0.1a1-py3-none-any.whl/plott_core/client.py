"""Plott Analytics client for event tracking and batching."""

import os
import asyncio
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
import httpx

from .types import PlottConfig, SDKMetadata, EventBatchRequest
from .events import (
    ErrorDetails,
    create_message_event,
    create_state_snapshot_event,
    create_error_event,
    create_run_event,
    create_tool_event,
    create_llm_call_event,
    create_custom_event,
)


class PlottAnalytics:
    """
    Plott Analytics client for tracking events with batching and retry support.

    Example:
        client = PlottAnalytics({"api_key": "cpk_..."})
        client.track_message_event(role="user", content="Hello")
        await client.flush()
        await client.shutdown()
    """

    def __init__(self, config: PlottConfig):
        """
        Initialize the Plott Analytics client.

        Args:
            config: Configuration dictionary with api_key and optional settings.

        Raises:
            ValueError: If api_key is missing or invalid.
        """
        api_key = config.get("api_key")
        if not api_key:
            raise ValueError("[Plott] API key is required")

        if not api_key.startswith("cpk_"):
            raise ValueError("[Plott] Invalid API key format. API key must start with 'cpk_'")

        # Determine environment
        environment = config.get("environment") or os.environ.get("NODE_ENV", "production")

        # Store resolved config with defaults
        self._api_key = api_key
        self._base_url = config.get("base_url") or os.environ.get("PLOTT_API_PATH", "https://api.plott.ai")
        self._batch_size = config.get("batch_size", 10)
        self._flush_interval = config.get("flush_interval", 1)
        self._retry_attempts = config.get("retry_attempts", 5)
        self._retry_delay = config.get("retry_delay", 1.0)
        self._debug = config.get("debug", False)
        self._environment = environment

        # SDK metadata
        self._metadata: SDKMetadata = {
            "sdk_version": "0.1.0",
            "framework": "core",
            "language": "python",
            "runtime": "python",
            "environment": environment,
        }

        # Event queue and state
        self._queue: List[Dict[str, Any]] = []
        self._in_flight_queue: Optional[List[Dict[str, Any]]] = None
        self._is_shutting_down = False
        self._is_flushing = False
        self._flush_task: Optional[asyncio.Task] = None
        self._timer_task: Optional[asyncio.Task] = None
        self._http_client: Optional[httpx.AsyncClient] = None

        if self._debug:
            print("[Plott] SDK initialized successfully")

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure HTTP client is initialized."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def _start_batching(self):
        """Start the background flush timer."""
        if self._timer_task is not None:
            return

        async def timer_loop():
            while not self._is_shutting_down:
                await asyncio.sleep(self._flush_interval)
                if not self._is_shutting_down:
                    await self.flush()

        self._timer_task = asyncio.create_task(timer_loop())

    def track(self, event: Dict[str, Any]) -> None:
        """
        Track a single event by adding it to the queue.

        Args:
            event: Event dictionary to track.
        """
        if self._is_shutting_down:
            if self._debug:
                print("[Plott] Cannot track events after shutdown")
            return

        # Add timestamp and context
        # Space out timestamps by 1ms based on queue length to ensure unique ordering within a batch
        timestamp = event.get("timestamp")
        if not timestamp:
            base_time = datetime.utcnow() + timedelta(milliseconds=len(self._queue))
            timestamp = base_time.isoformat(timespec='milliseconds') + "Z"

        event_with_meta = {
            **event,
            "timestamp": timestamp,
            "context": {
                **event.get("context", {}),
                "sdk_environment": self._environment,
            },
        }

        self._queue.append(event_with_meta)

        if self._debug:
            print(f"[Plott] Event queued: {event.get('type')}")


        # Auto-flush if batch size reached
        if len(self._queue) >= self._batch_size:
            # Schedule flush in background - handle both sync and async contexts
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.flush())
            except RuntimeError:
                # No running event loop - run flush synchronously in a new event loop
                print(f"[Plott] No running loop, running flush synchronously")
                asyncio.run(self.flush())

    def track_message_event(
        self,
        role: str,
        content: str,
        *,
        run_id: Optional[str] = None,
        session_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        token_count: Optional[int] = None,
        model: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track a message event."""
        self.track(create_message_event(
            role=role,
            content=content,
            run_id=run_id,
            session_id=session_id,
            turn_id=turn_id,
            token_count=token_count,
            model=model,
            context=context,
        ))

    def track_state_snapshot_event(
        self,
        snapshot: Dict[str, Any],
        role: str,
        *,
        run_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track a state snapshot event."""
        self.track(create_state_snapshot_event(
            snapshot=snapshot,
            role=role,
            run_id=run_id,
            session_id=session_id,
            context=context,
        ))

    def track_error_event(
        self,
        error: ErrorDetails,
        *,
        run_id: Optional[str] = None,
        session_id: Optional[str] = None,
        severity: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track an error event."""
        self.track(create_error_event(
            error=error,
            run_id=run_id,
            session_id=session_id,
            severity=severity,
            context=context,
        ))

    def track_run_event(
        self,
        value: str,
        *,
        run_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track a run event (start/end/resume)."""
        self.track(create_run_event(
            value=value,
            run_id=run_id,
            session_id=session_id,
            context=context,
        ))

    def track_tool_event(
        self,
        tool_call_id: str,
        tool_status: str,
        *,
        tool_name: Optional[str] = None,
        args: Optional[Union[Dict[str, Any], str]] = None,
        result: Optional[str] = None,
        error: Optional[str] = None,
        run_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track a tool event."""
        self.track(create_tool_event(
            tool_call_id=tool_call_id,
            tool_status=tool_status,
            tool_name=tool_name,
            args=args,
            result=result,
            error=error,
            run_id=run_id,
            session_id=session_id,
            context=context,
        ))

    def track_llm_call_event(
        self,
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
    ) -> None:
        """Track an LLM call event."""
        self.track(create_llm_call_event(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            provider=provider,
            finish_reason=finish_reason,
            is_streaming=is_streaming,
            first_token_latency_ms=first_token_latency_ms,
            run_id=run_id,
            session_id=session_id,
            context=context,
        ))

    def track_custom_event(
        self,
        value: Any,
        *,
        run_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track a custom event."""
        self.track(create_custom_event(
            value=value,
            run_id=run_id,
            session_id=session_id,
            context=context,
        ))

    async def flush(self) -> None:
        """Manually flush all queued events."""
        # Prevent concurrent flushes
        if self._is_flushing or len(self._queue) == 0:
            return

        self._is_flushing = True

        try:
            # Move current queue to in-flight, start fresh queue
            self._in_flight_queue = self._queue
            self._queue = []

            batch: EventBatchRequest = {
                "events": self._in_flight_queue,
                "batch_id": str(uuid.uuid4()),
            }

            await self._send_batch(batch)

            # Success - discard in-flight queue
            self._in_flight_queue = None

            if self._debug:
                print(f"[Plott] Successfully flushed {len(batch['events'])} events")

        except Exception as error:
            # Failed - restore in-flight events to front of queue
            if self._in_flight_queue:
                self._queue = self._in_flight_queue + self._queue
                self._in_flight_queue = None

            if self._debug:
                print(f"[Plott] Failed to flush events, restored to queue: {error}")

        finally:
            self._is_flushing = False

    async def _send_batch(self, batch: EventBatchRequest) -> None:
        """Send a batch of events to the API with retry logic."""
        client = await self._ensure_client()
        attempt = 0

        while attempt < self._retry_attempts:
            try:
                response = await client.post(
                    f"{self._base_url}/v1/ingest/events/batch",
                    json=batch,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self._api_key}",
                        "User-Agent": f"plott-sdk-core-python/{self._metadata['sdk_version']}",
                    },
                )

                if response.status_code >= 400:
                    error_text = response.text
                    raise Exception(f"HTTP {response.status_code}: {response.reason_phrase} - {error_text}")

                result = response.json()

                # Handle both unified and legacy response formats
                data = result.get("data", result)

                if self._debug:
                    print(f"[Plott] Batch sent successfully: {data}")

                if not data.get("batch_id") and not data.get("batchId"):
                    raise Exception("Invalid response format from server")

                return

            except Exception as error:
                if self._debug:
                    print(f"[Plott] Attempt {attempt + 1} failed: {error}")

                attempt += 1

                if attempt >= self._retry_attempts:
                    if self._debug:
                        print(f"[Plott] Max retries exceeded, events lost: {len(batch['events'])}")
                    return

                # Exponential backoff
                delay = self._retry_delay * (2 ** (attempt - 1))
                await asyncio.sleep(delay)

    async def shutdown(self) -> None:
        """Shutdown the client and flush any remaining events."""
        self._is_shutting_down = True

        # Cancel timer task
        if self._timer_task is not None:
            self._timer_task.cancel()
            try:
                await self._timer_task
            except asyncio.CancelledError:
                pass
            self._timer_task = None

        # Final flush
        await self.flush()

        # Close HTTP client
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None
