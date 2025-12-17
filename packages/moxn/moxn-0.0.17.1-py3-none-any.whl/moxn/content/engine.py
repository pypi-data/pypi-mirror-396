import asyncio
import heapq
import time
import weakref
from datetime import datetime, timezone
from typing import Generic, TypeVar

from moxn.base_models.blocks.signed import SignedURLContent
from moxn.content.backend import ContentBackend
from moxn.content.models import RefreshCfg
from moxn.types.content import SignedURLContentRequest

T = TypeVar("T", bound=SignedURLContent)


class RefreshEngine(Generic[T]):
    def __init__(
        self,
        backend: ContentBackend,
        refresh_cfg: RefreshCfg | None = None,
    ):
        refresh_cfg = refresh_cfg or RefreshCfg()
        self._refresh_cfg = refresh_cfg
        self._backend = backend
        self._heap: list[tuple[float, str]] = []
        self._refs: dict[str, weakref.ref[T]] = {}
        self._semaphore = asyncio.Semaphore(refresh_cfg.concurrency)
        self._bg: asyncio.Task | None = None
        self._shutdown = asyncio.Event()
        self._work_event = asyncio.Event()

    async def start(self) -> None:
        if self._bg:  # already running
            return
        self._bg = asyncio.create_task(self._loop(), name="refresh-engine")

    async def stop(self, *, deadline: float = 5.0) -> None:
        if not self._bg:
            return

        # Signal the loop to shutdown
        self._shutdown.set()
        # Also set work event to unblock waiting
        self._work_event.set()

        try:
            # Wait for graceful shutdown
            await asyncio.wait_for(self._bg, deadline)
        except asyncio.TimeoutError:
            # If timeout, cancel and suppress further errors
            self._bg.cancel()
            try:
                await self._bg
            except asyncio.CancelledError:
                pass  # Suppress the cancellation error
        finally:
            self._bg = None

    async def register(self, content: T) -> None:
        """Register content with the refresh engine.

        This adds the content to the tracking system but doesn't refresh it immediately
        unless it needs refreshing.
        """
        self._refs[content.file_path] = weakref.ref(content)

        # Only schedule if the content has a valid expiration
        # If not, we'll need to get one via refresh
        needs_immediate_refresh = content.expiration is None or content.should_refresh()

        if needs_immediate_refresh:
            # Don't schedule - refresh immediately to get a valid expiration
            await self._refresh_item(content)
        else:
            # Content has valid expiration, just schedule future refresh
            expiration = self._ensure_timezone_aware(content.expiration)
            refresh_time = self._schedule_refresh_time(expiration.timestamp())
            heapq.heappush(self._heap, (refresh_time, content.file_path))
            self._work_event.set()

    async def maybe_refresh(self, content: T) -> T:
        if not content.should_refresh():
            return content
        return await self._refresh_item(content)

    # internal -----------------
    async def _loop(self) -> None:
        while not self._shutdown.is_set():
            # Check shutdown signal before proceeding
            if self._shutdown.is_set():
                break

            await self._drain_due_items()

            try:
                # Check shutdown flag again before waiting
                if self._shutdown.is_set():
                    break

                await asyncio.wait_for(self._work_event.wait(), self._refresh_cfg.tick)
            except asyncio.TimeoutError:
                pass
            except asyncio.CancelledError:
                # Handle cancellation gracefully
                break
            self._work_event.clear()

    async def _drain_due_items(self) -> None:
        # Check shutdown signal early
        if self._shutdown.is_set():
            return

        now = time.monotonic()
        batch: list[T] = []
        while (
            self._heap
            and len(batch) < self._refresh_cfg.max_batch
            and self._heap[0][0] <= now
            and not self._shutdown.is_set()  # Add shutdown check in the loop
        ):
            _, key = heapq.heappop(self._heap)
            ref = self._refs.get(key)
            item = ref() if ref else None
            if item:
                batch.append(item)

        if batch and not self._shutdown.is_set():  # Check shutdown before refreshing
            await self._refresh_batch(batch)

    async def _refresh_item(self, content: T) -> T:
        try:
            # Use timeout from settings
            async with asyncio.timeout(self._refresh_cfg.refresh_timeout):
                async with self._semaphore:
                    response = await self._backend.get_signed_content_url(
                        SignedURLContentRequest(
                            file_path=content.file_path,
                            media_type=content.media_type,
                            ttl_seconds=content.ttl_seconds,
                        )
                    )
                    # Update the content with the new URL and expiration
                    content.signed_url = response.signed_url

                    # Ensure we store the expiration with timezone info
                    if response.expiration and response.expiration.tzinfo is None:
                        content.expiration = response.expiration.replace(
                            tzinfo=timezone.utc
                        )
                    else:
                        content.expiration = response.expiration

                    # Calculate refresh time with proper timezone handling
                    refresh_time = self._schedule_refresh_time(
                        self._ensure_timezone_aware(content.expiration).timestamp()
                    )
                    heapq.heappush(self._heap, (refresh_time, content.file_path))
                    self._work_event.set()

                    return content
        except (asyncio.TimeoutError, Exception) as e:
            # Log error and return original content
            import logging

            logging.error(f"Failed to refresh content {content.file_path}: {e}")
            return content

    async def _refresh_batch(self, items: list[T]) -> list[T]:
        if not items or self._shutdown.is_set():
            return items

        # Prepare requests safely
        try:
            reqs = [
                SignedURLContentRequest(
                    file_path=i.file_path,
                    media_type=i.media_type,
                    ttl_seconds=i.ttl_seconds,
                )
                for i in items
                if not self._shutdown.is_set()
            ]
        except Exception as e:
            import logging

            logging.error(f"Error preparing batch refresh requests: {e}")
            return items

        if not reqs or self._shutdown.is_set():
            return items

        # Use timeout from settings
        try:
            # Use semaphore to limit concurrency, but don't block the entire batch
            async with asyncio.timeout(self._refresh_cfg.refresh_timeout):
                async with self._semaphore:
                    resps = await self._backend.get_signed_content_url_batch(reqs)

            # Update each item and reschedule
            for itm, resp in zip(items, resps, strict=True):
                if self._shutdown.is_set():
                    break

                itm.signed_url, itm.expiration = resp.signed_url, resp.expiration

                # Re-schedule using our helper method
                refresh_time = self._schedule_refresh_time(itm.expiration.timestamp())
                heapq.heappush(self._heap, (refresh_time, itm.file_path))
                self._work_event.set()

            return items
        except (asyncio.TimeoutError, Exception) as e:
            import logging

            logging.error(f"Error in batch refresh: {e}")
            return items

    def _ensure_timezone_aware(
        self, dt: datetime | None, coerce_now: bool = True
    ) -> datetime:
        """Ensure datetime is timezone-aware, converting to UTC if it's naive"""
        if dt is None and coerce_now:
            _dt = datetime.now(timezone.utc)
        elif dt is not None:
            _dt = dt
        else:
            raise ValueError("dt is None and coerce_now is False")

        if _dt.tzinfo is None:
            # Convert naive datetime to UTC
            return _dt.replace(tzinfo=timezone.utc)
        return _dt

    def _schedule_refresh_time(self, expiration_timestamp: float) -> float:
        """Calculate the monotonic time when we should refresh the content.

        This ensures we refresh before the expiration time by applying the buffer.
        """
        # Current wall clock time (in UTC)
        now_wall = datetime.now(timezone.utc).timestamp()

        # Calculate time until expiration in seconds
        wall_time_delta = expiration_timestamp - now_wall

        # Apply the configured buffer (refresh before expiration)
        delta = wall_time_delta - self._refresh_cfg.buffer

        # Never schedule sooner than min_refresh_interval to avoid busy loops
        effective_delta = max(self._refresh_cfg.min_refresh_interval, delta)

        # Calculate the monotonic time when we should refresh
        refresh_at_monotonic = time.monotonic() + effective_delta

        return refresh_at_monotonic
