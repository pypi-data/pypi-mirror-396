"""W3C-compatible trace context management for the Moxn SDK.

This module provides:
- ContextVar management for async-safe span tracking
- Propagation helpers for injecting/extracting trace context from HTTP headers
- Utilities for cross-service trace correlation
"""

from __future__ import annotations

from contextvars import ContextVar, Token
from typing import TYPE_CHECKING
from uuid import UUID

from moxn.types.telemetry import (
    MoxnTraceCarrier,
    Span,
    SpanContext,
    TraceContext,
)

if TYPE_CHECKING:
    pass

# =============================================================================
# ContextVar Management
# =============================================================================

# Current active span (per-coroutine, async-safe)
current_span: ContextVar[Span | None] = ContextVar("current_span", default=None)


def get_current_span() -> Span | None:
    """Get the current active span, if any."""
    return current_span.get()


def get_current_span_context() -> SpanContext | None:
    """Get the SpanContext of the current span, if any."""
    span = current_span.get()
    return span.context if span else None


def get_current_trace_context() -> TraceContext | None:
    """Get the TraceContext of the current span, if any."""
    span = current_span.get()
    return span.context.trace_context if span else None


def set_span(span: Span) -> Token:
    """Set the current span. Returns token for reset."""
    return current_span.set(span)


def reset_span(token: Token) -> None:
    """Reset span to previous value using token."""
    current_span.reset(token)


# =============================================================================
# HTTP Header Propagation
# =============================================================================


def inject_headers(headers: dict[str, str] | None = None) -> dict[str, str]:
    """Inject current trace context into HTTP headers.

    Uses W3C Trace Context format (traceparent, tracestate).

    Args:
        headers: Existing headers dict to update. If None, creates new dict.

    Returns:
        Headers dict with traceparent (and optionally tracestate) added.
        Returns unchanged/empty dict if no active span.

    Example:
        >>> headers = inject_headers({})
        >>> # headers = {"traceparent": "00-0af7651916cd43dd...-01"}
        >>> response = await httpx.post(url, headers=headers)
    """
    if headers is None:
        headers = {}

    span = current_span.get()
    if span:
        headers.update(span.context.to_headers())

    return headers


def extract_span_context(headers: dict[str, str]) -> SpanContext | None:
    """Extract SpanContext from W3C trace context headers.

    Args:
        headers: HTTP headers dict containing traceparent (and optionally tracestate)

    Returns:
        SpanContext if traceparent header present and valid, None otherwise.
        The returned SpanContext has is_remote=True.

    Example:
        >>> span_ctx = extract_span_context(dict(request.headers))
        >>> if span_ctx:
        ...     async with client.span(session, trace_context=span_ctx.trace_context):
        ...         return await handle_request()
    """
    return SpanContext.from_headers(headers)


def extract_trace_context(headers: dict[str, str]) -> TraceContext | None:
    """Extract TraceContext from W3C trace context headers.

    This is a convenience wrapper around extract_span_context that
    returns just the TraceContext for starting a new root span in
    an existing trace.

    Args:
        headers: HTTP headers dict containing traceparent

    Returns:
        TraceContext if traceparent header present and valid, None otherwise.
    """
    span_ctx = SpanContext.from_headers(headers)
    return span_ctx.trace_context if span_ctx else None


def extract_carrier(
    headers: dict[str, str],
    prompt_id: UUID,
    prompt_name: str,
    task_id: UUID,
    commit_id: UUID | None,
    branch_id: UUID | None,
) -> MoxnTraceCarrier | None:
    """Extract trace context from headers and bundle with Moxn context.

    Use this when receiving a request and you want to create a full
    MoxnTraceCarrier for use with span_from_carrier().

    Args:
        headers: HTTP headers containing traceparent
        prompt_id: The prompt ID to associate with the carrier
        prompt_name: The prompt name
        task_id: The task ID
        commit_id: Commit ID (mutually exclusive with branch_id)
        branch_id: Branch ID (mutually exclusive with commit_id)

    Returns:
        MoxnTraceCarrier if traceparent present, None otherwise.
    """
    span_ctx = SpanContext.from_headers(headers)
    if span_ctx is None:
        return None

    return MoxnTraceCarrier(
        span_context=span_ctx,
        prompt_id=prompt_id,
        prompt_name=prompt_name,
        task_id=task_id,
        commit_id=commit_id,
        branch_id=branch_id,
    )
