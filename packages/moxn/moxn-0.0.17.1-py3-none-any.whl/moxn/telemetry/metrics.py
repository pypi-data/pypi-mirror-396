"""
Telemetry metrics collection for monitoring system health.

This module provides client-side metrics collection for the telemetry system,
tracking spans, events, timing, and errors to help detect issues like
dropped events or race conditions.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import threading
from typing import Any


@dataclass
class TelemetryMetrics:
    """Client-side telemetry metrics for monitoring system health."""

    # Counters
    spans_created: int = 0
    spans_completed: int = 0
    spans_failed: int = 0
    events_enqueued: int = 0
    events_dispatched: int = 0
    events_dropped: int = 0

    # Timing
    total_enqueue_time: float = 0.0
    total_dispatch_time: float = 0.0

    # Errors
    sequence_errors: int = 0
    context_errors: int = 0
    dispatch_errors: int = 0

    # Per-trace metrics
    trace_metrics: dict[str, dict] = field(default_factory=dict)

    _lock: threading.Lock = field(default_factory=threading.Lock)

    def record_span_created(self, trace_id: str) -> None:
        """Record that a span was created."""
        with self._lock:
            self.spans_created += 1
            if trace_id not in self.trace_metrics:
                self.trace_metrics[trace_id] = {
                    "spans": 0,
                    "events": 0,
                    "created_at": datetime.now(timezone.utc),
                }
            self.trace_metrics[trace_id]["spans"] += 1

    def record_span_completed(self, trace_id: str) -> None:
        """Record that a span completed successfully."""
        with self._lock:
            self.spans_completed += 1

    def record_span_failed(self, trace_id: str) -> None:
        """Record that a span failed with an error."""
        with self._lock:
            self.spans_failed += 1

    def record_event_enqueued(
        self, trace_id: str | None = None, enqueue_time: float = 0.0
    ) -> None:
        """Record that an event was enqueued for dispatch."""
        with self._lock:
            self.events_enqueued += 1
            self.total_enqueue_time += enqueue_time
            if trace_id and trace_id in self.trace_metrics:
                self.trace_metrics[trace_id]["events"] += 1

    def record_event_dispatched(self, dispatch_time: float = 0.0) -> None:
        """Record that an event was successfully dispatched."""
        with self._lock:
            self.events_dispatched += 1
            self.total_dispatch_time += dispatch_time

    def record_event_dropped(self) -> None:
        """Record that an event was dropped (not dispatched)."""
        with self._lock:
            self.events_dropped += 1

    def record_sequence_error(self) -> None:
        """Record a sequence number generation error."""
        with self._lock:
            self.sequence_errors += 1

    def record_context_error(self) -> None:
        """Record a span context management error."""
        with self._lock:
            self.context_errors += 1

    def record_dispatch_error(self) -> None:
        """Record a dispatch/backend error."""
        with self._lock:
            self.dispatch_errors += 1

    def get_summary(self) -> dict[str, Any]:
        """Get metrics summary for monitoring and diagnostics."""
        in_flight = self.events_enqueued - self.events_dispatched - self.events_dropped

        return {
            "spans": {
                "created": self.spans_created,
                "completed": self.spans_completed,
                "failed": self.spans_failed,
                "completion_rate": (
                    self.spans_completed / self.spans_created * 100
                    if self.spans_created > 0
                    else 0.0
                ),
            },
            "events": {
                "enqueued": self.events_enqueued,
                "dispatched": self.events_dispatched,
                "dropped": self.events_dropped,
                "in_flight": in_flight,
                "drop_rate": (
                    self.events_dropped / self.events_enqueued * 100
                    if self.events_enqueued > 0
                    else 0.0
                ),
            },
            "timing": {
                "avg_enqueue_time_ms": (
                    self.total_enqueue_time / self.events_enqueued * 1000
                    if self.events_enqueued > 0
                    else 0.0
                ),
                "avg_dispatch_time_ms": (
                    self.total_dispatch_time / self.events_dispatched * 1000
                    if self.events_dispatched > 0
                    else 0.0
                ),
            },
            "errors": {
                "sequence": self.sequence_errors,
                "context": self.context_errors,
                "dispatch": self.dispatch_errors,
                "total": self.sequence_errors
                + self.context_errors
                + self.dispatch_errors,
            },
            "traces": {
                "count": len(self.trace_metrics),
                "details": self.trace_metrics,
            },
            "health": self._calculate_health_status(),
        }

    def _calculate_health_status(self) -> str:
        """Calculate overall health status based on metrics."""
        if self.events_dropped > 0:
            drop_rate = (
                self.events_dropped / self.events_enqueued
                if self.events_enqueued > 0
                else 0
            )
            if drop_rate > 0.1:  # >10% drop rate
                return "critical"
            elif drop_rate > 0.05:  # >5% drop rate
                return "degraded"
            else:
                return "warning"

        total_errors = self.sequence_errors + self.context_errors + self.dispatch_errors
        if total_errors > 0:
            return "warning"

        in_flight = self.events_enqueued - self.events_dispatched - self.events_dropped
        if in_flight > 1000:  # High backlog
            return "degraded"
        elif in_flight > 100:
            return "warning"

        return "healthy"

    def reset(self) -> None:
        """Reset all metrics to zero (useful for testing)."""
        self.spans_created = 0
        self.spans_completed = 0
        self.spans_failed = 0
        self.events_enqueued = 0
        self.events_dispatched = 0
        self.events_dropped = 0
        self.total_enqueue_time = 0.0
        self.total_dispatch_time = 0.0
        self.sequence_errors = 0
        self.context_errors = 0
        self.dispatch_errors = 0
        self.trace_metrics.clear()


# Global metrics instance
_metrics = TelemetryMetrics()


def get_metrics() -> TelemetryMetrics:
    """Get the global telemetry metrics instance."""
    return _metrics


def reset_metrics() -> None:
    """Reset the global metrics (useful for testing)."""
    _metrics.reset()
