from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import uuid4

import httpx
from pydantic import BaseModel, HttpUrl, PrivateAttr, SecretStr, TypeAdapter

# TypeAdapter for serializing dicts that may contain Pydantic models
_content_adapter: TypeAdapter[dict[str, Any]] = TypeAdapter(dict[str, Any])

from moxn.settings import MoxnSettings, get_moxn_settings
from moxn.types.telemetry import (
    MAX_INLINE_CONTENT_SIZE,
    SignedURLRequest,
    SignedURLResponse,
    TelemetryLogRequest,
    TelemetryLogResponse,
)


class TelemetryTransportBackend(Protocol):
    """Protocol for the backend that handles actual sending of telemetry data"""

    async def send_telemetry_log(
        self, log_request: TelemetryLogRequest
    ) -> TelemetryLogResponse:
        """Send a telemetry log request"""
        ...

    async def aclose(self) -> None:
        """Close the backend and cleanup resources"""
        ...


class HttpTelemetryBackend(BaseModel):
    """
    Concrete implementation that talks to the Moxn API over HTTP,
    reusing a single AsyncClient for all telemetry posts and
    a second anonymous client for external-attributes PUTs.
    """

    api_key: SecretStr
    base_url: HttpUrl

    timeout: float = get_moxn_settings().telemetry_timeout

    # these clients are not part of the pydantic model, just PrivateAttrs
    _client: httpx.AsyncClient = PrivateAttr()
    _anon_client: httpx.AsyncClient = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        # 1) main client with base_url and auth headers baked in
        self._client = httpx.AsyncClient(
            base_url=str(self.base_url),
            timeout=self.timeout,
            headers=self.get_headers(),
        )
        # 2) anonymous client for external uploads (no base_url, no auth headers)
        self._anon_client = httpx.AsyncClient(timeout=self.timeout)

    @classmethod
    def from_settings(cls, settings: MoxnSettings) -> "HttpTelemetryBackend":
        return cls(
            base_url=settings.base_api_route,
            api_key=settings.api_key,
            timeout=settings.telemetry_timeout,
        )

    def get_headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key.get_secret_value(),
            "Content-Type": "application/json",
        }

    # ---------- public-protocol methods --------------------------------------

    async def send_telemetry_log(
        self, log_request: TelemetryLogRequest
    ) -> TelemetryLogResponse:
        """Send a telemetry log, delegating content to storage if too large"""

        # Check if content should be stored externally
        if log_request.content and self._should_use_external_storage(
            log_request.content
        ):
            return await self._send_telemetry_log_with_external_content(log_request)

        # inline case: use the persistent client with base_url
        resp = await self._client.post(
            "/telemetry/log-event",
            json=log_request.model_dump(exclude_none=True, mode="json", by_alias=True),
        )
        resp.raise_for_status()
        return TelemetryLogResponse.model_validate(resp.json())

    async def _send_telemetry_log_and_get_signed_url(
        self, req: SignedURLRequest
    ) -> SignedURLResponse:
        resp = await self._client.post(
            "/telemetry/log-event-and-get-signed-url",
            json=req.model_dump(exclude_none=True, mode="json", by_alias=True),
        )
        resp.raise_for_status()
        return SignedURLResponse.model_validate(resp.json())

    # ---------- internal helpers ---------------------------------------------

    def _extract_tenant_id_from_api_key(self) -> str:
        """Extract tenant ID from API key format: moxn_{tenant_id}.{rest}"""
        api_key_value = self.api_key.get_secret_value()

        # API keys are in format: moxn_{tenant_id}.{rest}
        # Extract the part after 'moxn_' and before the next dot
        if not api_key_value.startswith("moxn_"):
            raise ValueError("Invalid API key format - must start with 'moxn_'")

        # Remove 'moxn_' prefix and get tenant part
        key_without_prefix = api_key_value[5:]  # Remove 'moxn_'
        tenant_id = key_without_prefix.split(".")[0]

        if not tenant_id:
            raise ValueError("Invalid API key format - no tenant ID found")

        return tenant_id

    @staticmethod
    def _should_use_external_storage(content: dict) -> bool:
        """Check if content should be stored externally based on size"""
        try:
            return len(_content_adapter.dump_json(content)) > MAX_INLINE_CONTENT_SIZE
        except (TypeError, ValueError):
            return True

    async def _send_telemetry_log_with_external_content(
        self, log_request: TelemetryLogRequest
    ) -> TelemetryLogResponse:
        """Send telemetry log with content stored externally"""
        original_content = log_request.content
        log_request.content = None  # Clear content from inline request
        log_request.content_stored = True

        # Extract tenant ID from API key (format: moxn_{tenant_id}.{rest})
        tenant_id = self._extract_tenant_id_from_api_key()

        # Create storage path based on event IDs
        event_id = log_request.id
        file_path = f"{tenant_id}/{log_request.span_id or event_id}/{event_id}.json"

        signed_req = SignedURLRequest(
            file_path=file_path,
            media_type="application/json",
            log_request=log_request,
        )
        signed_resp = await self._send_telemetry_log_and_get_signed_url(signed_req)

        # Debug logging
        import logging

        logger = logging.getLogger(__name__)
        logger.debug(f"Received signed URL from API: {signed_resp.url}")

        # Validate signed URL before attempting upload
        if not signed_resp.url:
            raise ValueError("Signed URL response is missing URL field")

        # Support multiple URL schemes for generic hosting scenarios
        VALID_URL_SCHEMES = [
            "http://",
            "https://",  # Standard web protocols
            "s3://",  # AWS S3
            "gs://",  # Google Cloud Storage
            "azblob://",  # Azure Blob Storage
            "file://",  # Local filesystem (for testing)
        ]

        # Allow custom schemes via environment variable
        import os

        custom_schemes = os.getenv("MOXN_TELEMETRY_CUSTOM_URL_SCHEMES", "").split(",")
        VALID_URL_SCHEMES.extend(
            [s.strip() + "://" for s in custom_schemes if s.strip()]
        )

        if not isinstance(signed_resp.url, str):
            raise ValueError(
                f"Signed URL must be a string, got {type(signed_resp.url)}"
            )

        # Check if URL starts with any valid scheme
        if not any(signed_resp.url.startswith(scheme) for scheme in VALID_URL_SCHEMES):
            # Try to parse it as a URL to see if it has a valid structure
            from urllib.parse import urlparse

            parsed = urlparse(signed_resp.url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(
                    f"Invalid signed URL format: {signed_resp.url}. "
                    f"Expected URL with one of these schemes: {', '.join(VALID_URL_SCHEMES)} "
                    "or set MOXN_TELEMETRY_CUSTOM_URL_SCHEMES environment variable."
                )

        # Set storage key in request
        log_request.content_storage_key = signed_resp.file_path

        # upload the content anonymously
        put_resp = await self._anon_client.put(
            signed_resp.url,
            content=_content_adapter.dump_json(original_content),
            headers={"Content-Type": "application/json"},
        )
        put_resp.raise_for_status()

        return TelemetryLogResponse(
            id=signed_resp.id or uuid4(),
            timestamp=datetime.now(timezone.utc),
        )

    async def aclose(self) -> None:
        """Properly close all underlying HTTPX clients."""
        await self._client.aclose()
        await self._anon_client.aclose()
