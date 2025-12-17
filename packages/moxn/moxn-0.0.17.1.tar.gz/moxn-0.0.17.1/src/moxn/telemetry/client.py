"""Telemetry client for tracking spans and LLM events.

This module provides the TelemetryClient which:
- Creates and manages spans with W3C trace context
- Logs LLM events with full content capture
- Supports distributed tracing via parent_context and trace_context parameters
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from contextvars import Token
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, AsyncGenerator, Optional
from uuid import uuid4

from pydantic_core import to_jsonable_python

from moxn.settings import MoxnSettings, get_moxn_settings
from moxn.telemetry.backend import HttpTelemetryBackend, TelemetryTransportBackend
from moxn.telemetry.context import (
    get_current_span,
    reset_span,
    set_span,
)
from moxn.telemetry.dispatcher import TelemetryDispatcher
from moxn.types.telemetry import (
    EVENT_TYPE_LLM_CALL,
    EVENT_TYPE_SPAN_END,
    EVENT_TYPE_SPAN_ERROR,
    EVENT_TYPE_SPAN_START,
    MoxnTraceCarrier,
    Span,
    SpanContext,
    TelemetryLogRequest,
    TraceContext,
)

if TYPE_CHECKING:
    from moxn.models.prompt import PromptSession
    from moxn.models.response import LLMEvent

logger = logging.getLogger(__name__)


class TelemetryClient:
    """Higher-level façade that tracks spans and delegates sending to a backend.

    Supports W3C Trace Context for distributed tracing:
    - parent_context: Explicit parent span for callbacks/async patterns
    - trace_context: Continue an existing trace from another service
    """

    def __init__(self, backend: TelemetryTransportBackend) -> None:
        self._backend = backend
        self._dispatcher = TelemetryDispatcher(backend)
        self._started = False

    @classmethod
    def from_settings(cls, settings: MoxnSettings) -> TelemetryClient:
        backend = HttpTelemetryBackend.from_settings(settings)
        return cls(backend)

    # ------------------------------------------------------------------ #
    # Lifecycle helpers
    # ------------------------------------------------------------------ #

    async def start(self) -> None:
        """Start the telemetry system with background workers."""
        if not self._started:
            await self._dispatcher.start()
            self._started = True

    async def stop(self) -> None:
        """Stop the telemetry system, flush pending items, and clean up resources."""
        if self._started:
            try:
                await self._dispatcher.flush(timeout=get_moxn_settings().timeout)
            except asyncio.TimeoutError:
                pass
            await self._dispatcher.stop()
            self._started = False

        if hasattr(self._backend, "aclose"):
            await self._backend.aclose()

    async def __aenter__(self) -> TelemetryClient:
        await self.start()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.stop()

    # ------------------------------------------------------------------ #
    # Span Management
    # ------------------------------------------------------------------ #

    @asynccontextmanager
    async def span(
        self,
        prompt_session: PromptSession,
        name: str | None = None,
        metadata: Optional[dict[str, Any]] = None,
        *,
        parent_context: SpanContext | None = None,
        trace_context: TraceContext | None = None,
    ) -> AsyncGenerator[Span, None]:
        """Create a span for tracking work.

        Context resolution order:
        1. parent_context parameter (explicit parent for callbacks)
        2. current_span ContextVar (automatic nesting)
        3. trace_context parameter (new root in existing trace)
        4. Generate new trace

        Args:
            prompt_session: The prompt session being executed
            name: Optional span name (defaults to prompt name)
            metadata: User-provided searchable attributes
            parent_context: Explicit parent SpanContext (for async/callback patterns)
            trace_context: Explicit TraceContext (for distributed tracing)

        Yields:
            Span: The active span for this context
        """
        if not self._started:
            await self.start()

        # Resolve parent context using priority order
        current = get_current_span()
        _name = name or prompt_session.prompt.name

        if parent_context is not None:
            # Explicit parent provided (e.g., from callback)
            span_ctx = SpanContext.create_child(parent_context)
            parent_span_id = parent_context.span_id
        elif current is not None:
            # Inherit from current span (automatic nesting)
            span_ctx = SpanContext.create_child(current.context)
            parent_span_id = current.span_id
        elif trace_context is not None:
            # New root span in existing trace (distributed tracing)
            span_ctx = SpanContext.create_root(trace_context)
            parent_span_id = None
        else:
            # Brand new trace
            span_ctx = SpanContext.create_root()
            parent_span_id = None

        # Create the Span object
        span = Span(
            context=span_ctx,
            name=_name,
            parent_span_id=parent_span_id,
            start_time=datetime.now(timezone.utc),
            prompt_id=prompt_session.prompt_id,
            prompt_name=prompt_session.prompt.name,
            task_id=prompt_session.prompt.task_id,
            commit_id=prompt_session.prompt.commit_id,
            branch_id=prompt_session.prompt.branch_id,
            attributes=metadata or {},
        )

        # Set as current span
        token: Token = set_span(span)

        # Log span start
        await self._log_span_start(span)

        try:
            yield span
        except Exception as exc:
            span.record_exception(exc)
            await self._log_span_error(span)
            raise
        finally:
            span.end()
            reset_span(token)
            await self._log_span_end(span)

    @asynccontextmanager
    async def span_from_carrier(
        self,
        carrier: MoxnTraceCarrier,
        name: str | None = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> AsyncGenerator[Span, None]:
        """Create a span that continues from a MoxnTraceCarrier.

        Use this when receiving trace context from another service
        or resuming a trace in a callback.

        Args:
            carrier: The trace carrier containing context and Moxn metadata
            name: Optional span name (defaults to prompt name from carrier)
            metadata: User-provided searchable attributes

        Yields:
            Span: The active span for this context
        """
        if not self._started:
            await self.start()

        # Create child span from carrier's span context
        span_ctx = SpanContext.create_child(carrier.span_context)

        span = Span(
            context=span_ctx,
            name=name or carrier.prompt_name,
            parent_span_id=carrier.span_id,
            start_time=datetime.now(timezone.utc),
            prompt_id=carrier.prompt_id,
            prompt_name=carrier.prompt_name,
            task_id=carrier.task_id,
            commit_id=carrier.commit_id,
            branch_id=carrier.branch_id,
            attributes=metadata or {},
        )

        token: Token = set_span(span)
        await self._log_span_start(span)

        try:
            yield span
        except Exception as exc:
            span.record_exception(exc)
            await self._log_span_error(span)
            raise
        finally:
            span.end()
            reset_span(token)
            await self._log_span_end(span)

    def extract_context(self) -> MoxnTraceCarrier | None:
        """Extract current span as a carrier for propagation.

        Returns:
            MoxnTraceCarrier if there's an active span, None otherwise.
        """
        span = get_current_span()
        if span is None:
            return None
        return span.extract_carrier()

    # ------------------------------------------------------------------ #
    # Event Logging
    # ------------------------------------------------------------------ #

    async def log_event(self, event: LLMEvent) -> None:
        """Log an LLM event within the current span or a transient span.

        Args:
            event: The LLM event to log
        """
        if not self._started:
            await self.start()

        span = get_current_span()

        if span is not None:
            await self._log_llm_event(span, event)
        else:
            await self._log_event_with_transient_span(event)

    async def _log_llm_event(self, span: Span, event: LLMEvent) -> None:
        """Log an LLM event within a span context."""
        system_metadata = self._build_llm_system_metadata(event, span)

        user_metadata = dict(span.attributes)
        if event.attributes:
            user_metadata.update(event.attributes)

        content = self._build_llm_content(event)

        await self._dispatcher.enqueue(
            TelemetryLogRequest(
                id=uuid4(),
                timestamp=datetime.now(timezone.utc),
                event_type=EVENT_TYPE_LLM_CALL,
                trace_id=span.trace_id,
                span_id=span.span_id,
                parent_span_id=span.parent_span_id,
                sequence_number=span.next_sequence(),
                prompt_id=span.prompt_id,
                task_id=span.task_id,
                commit_id=span.commit_id if span.commit_id else None,
                branch_id=span.branch_id if not span.commit_id else None,
                system_metadata=system_metadata,
                user_metadata=user_metadata,
                content=content,
            )
        )

    def _build_llm_system_metadata(self, event: LLMEvent, span: Span) -> dict[str, Any]:
        """Extract system metadata from LLM event."""
        metadata: dict[str, Any] = {
            "prompt.name": span.prompt_name,
            "llm.provider": event.provider.value if event.provider else None,
            "llm.response_type": event.response_type.value,
        }

        if event.parsed_response:
            metadata["llm.model"] = event.parsed_response.model
            if event.parsed_response.usage:
                metadata["llm.tokens.input"] = event.parsed_response.usage.input_tokens
                metadata["llm.tokens.output"] = (
                    event.parsed_response.usage.completion_tokens
                )

        if event.tool_calls_count > 0:
            metadata["llm.tool_calls_count"] = event.tool_calls_count

        return metadata

    def _build_llm_content(self, event: LLMEvent) -> dict[str, Any]:
        """Build LLM event content per backend specification.

        Structure (camelCase keys):
        - messages: Template messages
        - sessionData: Raw pydantic model for reconstruction
        - renderedInput: Final rendered variables (what was sent to LLM)
        - llmResponse:
            - rawResponse: Original provider response (as-is)
            - parsedResponse: Normalized with contentBlocks array
        """
        return {
            "messages": [
                m.model_dump(mode="json", by_alias=True) for m in event.messages
            ],
            "sessionData": (
                event.session_data.model_dump(mode="json", by_alias=True)
                if event.session_data
                else None
            ),
            "renderedInput": (
                to_jsonable_python(event.rendered_input, by_alias=True)
                if event.rendered_input
                else None
            ),
            "llmResponse": {
                "rawResponse": event.raw_response,
                "parsedResponse": (
                    # Exclude raw_response to avoid duplication (already at rawResponse above)
                    event.parsed_response.model_dump(
                        mode="json", by_alias=True, exclude={"raw_response"}
                    )
                    if event.parsed_response
                    else None
                ),
            },
        }

    async def _log_event_with_transient_span(self, event: LLMEvent) -> None:
        """Create a transient span just for logging a single LLM event.

        Since LLMEvent now has task_id as a required field, we can create
        transient spans without needing external session context.
        """
        # Create a transient span
        span_ctx = SpanContext.create_root()
        span = Span(
            context=span_ctx,
            name="llm_call",
            parent_span_id=None,
            start_time=datetime.now(timezone.utc),
            prompt_id=event.prompt_id,
            prompt_name=event.prompt_name,
            task_id=event.task_id,
            commit_id=event.commit_id,
            branch_id=event.branch_id,
            attributes={"transient": True},
        )

        await self._log_span_start(span)

        try:
            await self._log_llm_event(span, event)
        except Exception as exc:
            span.record_exception(exc)
            await self._log_span_error(span)
            raise
        finally:
            span.end()
            await self._log_span_end(span)

    # ------------------------------------------------------------------ #
    # Internal logging helpers
    # ------------------------------------------------------------------ #

    async def _log_span_start(self, span: Span) -> None:
        """Log span start event."""
        system_metadata = {
            "span.name": span.name,
            "prompt.name": span.prompt_name,
            "span.status": span.status.value,
        }

        await self._dispatcher.enqueue(
            TelemetryLogRequest(
                id=uuid4(),
                timestamp=span.start_time,
                event_type=EVENT_TYPE_SPAN_START,
                trace_id=span.trace_id,
                span_id=span.span_id,
                parent_span_id=span.parent_span_id,
                sequence_number=span.next_sequence(),
                prompt_id=span.prompt_id,
                task_id=span.task_id,
                commit_id=span.commit_id if span.commit_id else None,
                branch_id=span.branch_id if not span.commit_id else None,
                system_metadata=system_metadata,
                user_metadata=dict(span.attributes),
            )
        )

    async def _log_span_error(self, span: Span) -> None:
        """Log span error event."""
        system_metadata = {
            "span.name": span.name,
            "prompt.name": span.prompt_name,
            "span.status": span.status.value,
        }

        # Include error attributes if present
        if "error.message" in span.attributes:
            system_metadata["error.message"] = span.attributes["error.message"]
        if "error.type" in span.attributes:
            system_metadata["error.type"] = span.attributes["error.type"]

        await self._dispatcher.enqueue(
            TelemetryLogRequest(
                id=uuid4(),
                timestamp=datetime.now(timezone.utc),
                event_type=EVENT_TYPE_SPAN_ERROR,
                trace_id=span.trace_id,
                span_id=span.span_id,
                parent_span_id=span.parent_span_id,
                sequence_number=span.next_sequence(),
                prompt_id=span.prompt_id,
                task_id=span.task_id,
                commit_id=span.commit_id if span.commit_id else None,
                branch_id=span.branch_id if not span.commit_id else None,
                system_metadata=system_metadata,
                user_metadata=dict(span.attributes),
            )
        )

    async def _log_span_end(self, span: Span) -> None:
        """Log span end event."""
        system_metadata = {
            "span.name": span.name,
            "prompt.name": span.prompt_name,
            "span.status": span.status.value,
        }

        if span.duration_ms is not None:
            system_metadata["span.duration_ms"] = span.duration_ms

        await self._dispatcher.enqueue(
            TelemetryLogRequest(
                id=uuid4(),
                timestamp=span.end_time or datetime.now(timezone.utc),
                event_type=EVENT_TYPE_SPAN_END,
                trace_id=span.trace_id,
                span_id=span.span_id,
                parent_span_id=span.parent_span_id,
                sequence_number=span.next_sequence(),
                prompt_id=span.prompt_id,
                task_id=span.task_id,
                commit_id=span.commit_id if span.commit_id else None,
                branch_id=span.branch_id if not span.commit_id else None,
                system_metadata=system_metadata,
                user_metadata=dict(span.attributes),
            )
        )
