from __future__ import annotations

import logging
from typing import Protocol

import httpx
from pydantic import BaseModel, HttpUrl, PrivateAttr, SecretStr

from moxn.settings import MoxnSettings, get_moxn_settings
from moxn.types.content import (
    SignedURLContentRequest,
    SignedURLContentResponse,
)

logger = logging.getLogger(__name__)


class ContentBackend(Protocol):
    """Protocol for the backend that handles content API requests"""

    async def get_signed_content_url(
        self, request: SignedURLContentRequest
    ) -> SignedURLContentResponse: ...

    async def get_signed_content_url_batch(
        self, requests: list[SignedURLContentRequest]
    ) -> list[SignedURLContentResponse]: ...

    async def aclose(self) -> None: ...


class HttpContentBackend(BaseModel):
    """
    Concrete implementation that talks to the Moxn API over HTTP
    for content-related operations such as retrieving signed URLs.
    """

    api_key: SecretStr
    base_url: HttpUrl

    timeout: float = get_moxn_settings().timeout

    # HTTP client is not part of the pydantic model, just a PrivateAttr
    _client: httpx.AsyncClient = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        # Create client with base_url and auth headers baked in
        self._client = httpx.AsyncClient(
            base_url=str(self.base_url),
            timeout=self.timeout,
            headers=self.get_headers(),
        )

    @classmethod
    def from_settings(cls, settings: MoxnSettings) -> "HttpContentBackend":
        return cls(
            base_url=settings.base_api_route,
            api_key=settings.api_key,
            timeout=settings.timeout,
        )

    def get_headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key.get_secret_value(),
            "Content-Type": "application/json",
        }

    # Content API methods

    async def get_signed_content_url(
        self, request: SignedURLContentRequest
    ) -> SignedURLContentResponse:
        """
        Get a signed URL for a content item.

        Args:
            request: The request containing content key and TTL

        Returns:
            Response containing signed URL and expiration time
        """
        try:
            response = await self._client.post(
                "/content/signed-url",
                json=request.model_dump(exclude_none=True, mode="json", by_alias=True),
            )
            response.raise_for_status()

            # Unwrap the gateway response envelope
            response_data = response.json()
            if not response_data.get("success"):
                error_msg = response_data.get("error", "Unknown error")
                raise ValueError(f"Gateway returned error: {error_msg}")

            return SignedURLContentResponse.model_validate(response_data["data"])
        except Exception as e:
            logger.error(f"Error getting signed content URL: {e}", exc_info=True)
            raise

    async def get_signed_content_url_batch(
        self, requests: list[SignedURLContentRequest]
    ) -> list[SignedURLContentResponse]:
        """
        Get signed URLs for a batch of content items.

        Args:
            requests: List of requests containing content key and TTL

        Returns:
            List of responses containing signed URL and expiration time
        """
        try:
            response = await self._client.post(
                "/content/signed-url-batch",
                json=[
                    item.model_dump(exclude_none=True, mode="json", by_alias=True) for item in requests
                ],
            )
            response.raise_for_status()

            # Unwrap the gateway response envelope
            response_data = response.json()
            if not response_data.get("success"):
                error_msg = response_data.get("error", "Unknown error")
                raise ValueError(f"Gateway returned error: {error_msg}")

            return [
                SignedURLContentResponse.model_validate(item)
                for item in response_data["data"]
            ]
        except Exception as e:
            logger.error(f"Error getting signed content URL: {e}", exc_info=True)
            raise

    async def aclose(self) -> None:
        """Properly close the underlying HTTPX client."""
        await self._client.aclose()
