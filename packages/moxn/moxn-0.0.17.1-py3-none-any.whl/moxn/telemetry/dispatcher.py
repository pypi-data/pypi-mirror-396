from __future__ import annotations

import asyncio
import logging
import time
import traceback
from typing import Any, TypeAlias, TypeVar

from moxn.settings import get_moxn_settings
from moxn.telemetry.metrics import get_metrics
from moxn.types.telemetry import TelemetryLogRequest

_Sendable: TypeAlias = TelemetryLogRequest
T = TypeVar("T")
logger = logging.getLogger(__name__)


class TelemetryDispatcher:
    """
    Background-worker pool that delivers telemetry envelopes to the backend.

    Calls to `enqueue()` never block on I/O – they just put the envelope on
    an asyncio.Queue. One or more workers drain that queue.
    """

    def __init__(
        self,
        backend: Any,
        *,
        concurrency: int = 4,
        queue_maxsize: int = 10_000,
    ) -> None:
        self._backend = backend
        self._q: asyncio.Queue[_Sendable] = asyncio.Queue(maxsize=queue_maxsize)
        self._workers: list[asyncio.Task[None]] = []
        self._closing = asyncio.Event()
        self._concurrency = max(1, concurrency)
        # Add a debug counter to track pending items
        self._pending_count = 0
        self._debug = logger.isEnabledFor(logging.DEBUG)

        # Enhanced diagnostic tracking
        self._enqueue_count = 0
        self._dispatch_count = 0
        self._drop_count = 0
        self._error_count = 0

    async def __aenter__(self) -> "TelemetryDispatcher":
        await self.start()
        return self

    async def __aexit__(self, exc_t, exc, tb) -> None:
        await self.stop()

    # --------------------------------------------------------------------- #
    # public API
    # --------------------------------------------------------------------- #

    async def start(self) -> None:
        """Spawn background workers (idempotent)."""
        if self._workers:
            return
        for i in range(self._concurrency):
            self._workers.append(
                asyncio.create_task(self._worker(), name=f"telemetry-worker-{i}")
            )
        logger.debug(f"Started {len(self._workers)} telemetry workers")

    async def enqueue(self, item: _Sendable) -> bool:
        """
        Put an envelope on the queue without awaiting network I/O.
        Returns True if successfully enqueued, False if dropped.
        """
        start_time = time.time()
        metrics = get_metrics()

        # Extract trace_id for metrics (if it's a telemetry event)
        trace_id = None
        if hasattr(item, "events") and item.events:
            event = item.events[0]  # Usually single event per request
            if hasattr(event, "root_span_id"):
                trace_id = str(event.root_span_id) if event.root_span_id else None

        try:
            # Try to enqueue without blocking
            self._q.put_nowait(item)
            self._enqueue_count += 1
            self._pending_count += 1

            # Record metrics
            enqueue_time = time.time() - start_time
            metrics.record_event_enqueued(trace_id, enqueue_time)

            if self._debug:
                logger.debug(
                    f"ENQUEUE {self._enqueue_count}: {type(item).__name__} "
                    f"(queue_size={self._q.qsize()}, pending={self._pending_count})"
                )
            return True

        except asyncio.QueueFull:
            # Queue is full - log and drop
            self._drop_count += 1

            # Record dropped event
            metrics.record_event_dropped()

            logger.error(
                f"TELEMETRY DROP: Queue full (size={self._q.qsize()}) "
                f"dropping event {type(item).__name__}"
            )
            return False

    async def flush(self, timeout: float | None = get_moxn_settings().timeout) -> None:
        """
        Block until the queue is empty (or timeout).

        Use this in serverless handlers before returning.
        """
        if self._pending_count > 0 or not self._q.empty():
            logger.debug(
                f"Flushing {self._pending_count} pending telemetry items (timeout: {timeout}s)"
            )
            try:
                await asyncio.wait_for(self._q.join(), timeout=timeout)
                logger.debug("Telemetry queue flushed successfully")
            except asyncio.TimeoutError:
                logger.warning(
                    f"Flush timed out after {timeout}s with {self._pending_count} items remaining"
                )
                raise

    async def stop(self) -> None:
        """Flush and cancel workers."""
        try:
            # First try to flush with a reasonable timeout
            await self.flush(timeout=get_moxn_settings().timeout)
        except asyncio.TimeoutError:
            logger.warning("Failed to flush all telemetry before stopping")

        # Signal workers to stop and wait for them
        self._closing.set()
        if self._workers:
            logger.debug(f"Stopping {len(self._workers)} telemetry workers")
            for t in self._workers:
                t.cancel()
            await asyncio.gather(*self._workers, return_exceptions=True)
            self._workers.clear()
            logger.debug("All telemetry workers stopped")

    # --------------------------------------------------------------------- #
    # internal
    # --------------------------------------------------------------------- #

    async def _worker(self) -> None:
        """Worker loop that processes queue items."""
        logger.debug(
            f"Telemetry worker {getattr(asyncio.current_task(), 'get_name', lambda: 'unknown')} started"
        )

        while not self._closing.is_set():
            try:
                # Get the next item or wait for a closing signal
                item = await asyncio.wait_for(
                    self._q.get(),
                    timeout=0.5,  # Check for closing every 0.5s
                )
            except asyncio.TimeoutError:
                continue  # No items, check closing and try again
            except asyncio.CancelledError:
                logger.debug(
                    f"Worker {getattr(asyncio.current_task(), 'get_name', lambda: 'unknown')} cancelled"
                )
                break

            metrics = get_metrics()
            success = False
            dispatch_start = time.time()

            try:
                if self._debug:
                    logger.debug(f"DISPATCH START: {type(item).__name__}")

                # Actually send the telemetry (this is the part that can take time)
                await self._backend.send_telemetry_log(item)
                success = True

                self._dispatch_count += 1

                # Record successful dispatch
                dispatch_time = time.time() - dispatch_start
                metrics.record_event_dispatched(dispatch_time)

                if self._debug:
                    logger.debug(f"DISPATCH SUCCESS: {type(item).__name__}")
            except Exception as e:
                self._error_count += 1

                # Record dispatch error
                metrics.record_dispatch_error()

                logger.error(f"Failed to send telemetry: {e}\n{traceback.format_exc()}")
            finally:
                # CRITICAL: Mark the item as done regardless of success/failure
                # This is what makes q.join() resolve when the queue is empty
                self._q.task_done()
                self._pending_count -= 1

                if self._debug:
                    status = "✓" if success else "✗"
                    logger.debug(
                        f"{status} Completed {type(item).__name__} - "
                        f"remaining: {self._pending_count}"
                    )

        logger.debug(
            f"Telemetry worker {getattr(asyncio.current_task(), 'get_name', lambda: 'unknown')} exiting"
        )

    def get_diagnostics(self) -> dict:
        """Get diagnostic information about dispatcher state."""
        return {
            "enqueued": self._enqueue_count,
            "dispatched": self._dispatch_count,
            "dropped": self._drop_count,
            "errors": self._error_count,
            "queue_size": self._q.qsize(),
            "pending_count": self._pending_count,
            "workers": len(self._workers),
        }
