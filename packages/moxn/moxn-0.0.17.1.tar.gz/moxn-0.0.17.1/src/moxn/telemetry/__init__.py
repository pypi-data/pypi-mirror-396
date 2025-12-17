"""Telemetry module for distributed tracing and LLM event logging.

This module provides:
- W3C Trace Context compatible distributed tracing
- Span management for tracking LLM workflows
- HTTP header propagation utilities
- Context extraction for async/callback patterns

Types:
    TraceContext: Immutable trace identity (trace_id, trace_flags, trace_state)
    SpanContext: Immutable span reference for propagation
    Span: Active span with attributes and timing
    MoxnTraceCarrier: Full context carrier for cross-service propagation

Utilities:
    inject_headers: Add trace context to outgoing HTTP headers
    extract_span_context: Parse trace context from incoming headers
    extract_trace_context: Parse just TraceContext from headers
    get_current_span: Get the active span from ContextVar
"""

# Re-export types from moxn.types for convenience
from moxn.types.telemetry import (
    MoxnTraceCarrier,
    Span,
    SpanContext,
    SpanEvent,
    SpanLink,
    SpanStatus,
    TraceContext,
)

# Re-export context utilities
from moxn.telemetry.context import (
    extract_carrier,
    extract_span_context,
    extract_trace_context,
    get_current_span,
    get_current_span_context,
    get_current_trace_context,
    inject_headers,
)

# Re-export client
from moxn.telemetry.client import TelemetryClient

__all__ = [
    # Types
    "TraceContext",
    "SpanContext",
    "SpanStatus",
    "SpanEvent",
    "SpanLink",
    "Span",
    "MoxnTraceCarrier",
    # Context utilities
    "get_current_span",
    "get_current_span_context",
    "get_current_trace_context",
    "inject_headers",
    "extract_span_context",
    "extract_trace_context",
    "extract_carrier",
    # Client
    "TelemetryClient",
]
