from __future__ import annotations

import logging
from typing import TypeVar

from moxn.base_models.blocks.signed import SignedURLContent
from moxn.content.backend import ContentBackend, HttpContentBackend
from moxn.content.engine import RefreshEngine
from moxn.content.models import RefreshCfg
from moxn.settings import MoxnSettings

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=SignedURLContent)


class ContentClient:
    """
    Client for managing cached content with automatic refresh capabilities.

    This class handles registration, refreshing, and lifecycle management of
    cacheable content like signed URLs for contents and other media.
    """

    def __init__(self, backend: ContentBackend, refresh_cfg: RefreshCfg) -> None:
        """
        Initialize a content client with the given backend.

        Args:
            backend: The backend for making API requests
            refresh_cfg: Configuration for refresh behavior
        """
        self._backend = backend
        self._engine: RefreshEngine[SignedURLContent] = RefreshEngine(
            backend, refresh_cfg
        )
        self._started = False

    @classmethod
    def from_settings(cls, settings: MoxnSettings) -> "ContentClient":
        """Create a content client from settings."""
        backend = HttpContentBackend.from_settings(settings)

        # Create RefreshCfg from settings
        refresh_cfg = RefreshCfg(
            concurrency=settings.content_refresh_cfg_concurrency,
            buffer=settings.content_refresh_cfg_buffer,
            tick=settings.content_refresh_cfg_tick,
            max_batch=settings.content_refresh_cfg_max_batch,
            refresh_timeout=settings.content_refresh_cfg_refresh_timeout,
            min_refresh_interval=settings.content_refresh_cfg_min_refresh_interval,
        )

        return cls(backend, refresh_cfg)

    async def start(self) -> None:
        """Start the content client with background refresh capabilities."""
        if not self._started:
            self._started = True
            await self._engine.start()
            logger.info("Content client started")

    async def stop(self) -> None:
        """Stop the content client and clean up resources."""
        if self._started:
            logger.info("Stopping content client...")
            await self._engine.stop()
            await self._backend.aclose()
            self._started = False
            logger.info("Content client stopped")

    async def register_content(self, content: T) -> T:
        """
        Register content for automatic refresh management.

        Args:
            content: The content to register

        Returns:
            The registered content (same instance)
        """
        if not self._started:
            await self.start()

        await self._engine.register(content)
        return content

    async def maybe_refresh_content(
        self, content: SignedURLContent
    ) -> SignedURLContent:
        """
        Check if content needs refreshing and refresh if necessary.

        Args:
            content: The content to check and potentially refresh

        Returns:
            The refreshed content (or original if no refresh needed)
        """
        if not self._started:
            await self.start()

        if not content.should_refresh():
            return content

        return await self.refresh_item(content)

    async def refresh_item(self, content: SignedURLContent) -> SignedURLContent:
        """
        Refresh the signed URL for a content item.

        Args:
            content: The SignedURLContent object to refresh

        Returns:
            The SignedURLContent object with a fresh URL
        """
        try:
            # Delegate to the engine to handle the refresh properly
            # This ensures consistent behavior and proper rescheduling
            return await self._engine._refresh_item(content)
        except Exception as e:
            logger.error(f"Failed to refresh content: {e}", exc_info=True)
            # Return the original content even if refresh failed
            return content

    async def refresh_signed_url_content_batch(
        self, contents: list[SignedURLContent]
    ) -> list[SignedURLContent]:
        """
        Refresh multiple cached content in parallel.

        Args:
            contents: List of SignedURLContent objects to refresh

        Returns:
            List of SignedURLContent objects with fresh URLs
        """
        try:
            return await self._engine._refresh_batch(contents)
        except Exception as e:
            logger.error(f"Failed to refresh content batch: {e}", exc_info=True)
            return contents
