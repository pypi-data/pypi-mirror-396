"""Simplified tenant-based authentication models."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, SecretStr


class TenantAuth(BaseModel):
    """
    Tenant-scoped authentication via API key.

    Modern, simplified authentication that only requires an API key.
    The API key already contains the tenant context, eliminating the need
    for separate user_id, org_id, or tenant_id fields.

    Example:
        ```python
        auth = TenantAuth(api_key="moxn_3Oxskm27Fn...")
        headers = auth.to_headers()
        # {"x-api-key": "moxn_3Oxskm27Fn...", "Content-Type": "application/json"}
        ```
    """

    api_key: SecretStr

    def to_headers(self) -> dict[str, str]:
        """Convert to HTTP headers for API requests."""
        return {
            "x-api-key": self.api_key.get_secret_value(),
            "Content-Type": "application/json",
        }

    def __repr__(self) -> str:
        """Safe representation that doesn't expose the API key."""
        return "TenantAuth(api_key=SecretStr('**********'))"


class TenantInfo(BaseModel):
    """Tenant information from auth validation."""

    id: str
    name: str
    slug: str
    type: Literal["personal", "team"]
    plan_type: Literal["individual", "team", "enterprise"] = Field(alias="planType")
    subscription_status: Literal["active", "past_due", "canceled", "trialing"] = Field(
        alias="subscriptionStatus"
    )

    class Config:
        populate_by_name = True


class ApiKeyInfo(BaseModel):
    """API key information from auth validation."""

    id: str
    name: str
    scope: Literal["read", "write"]
    created_at: datetime = Field(alias="createdAt")
    expires_at: datetime | None = Field(alias="expiresAt", default=None)

    class Config:
        populate_by_name = True


class AuthValidationResponse(BaseModel):
    """Response from backend /api/v1/auth/verify endpoint."""

    valid: bool
    tenant: TenantInfo
    api_key: ApiKeyInfo = Field(alias="apiKey")

    class Config:
        populate_by_name = True


class CachedAuthInfo(BaseModel):
    """Cached auth information with TTL."""

    tenant_id: str
    tenant_name: str
    tenant_slug: str
    scope: Literal["read", "write"]
    subscription_status: Literal["active", "past_due", "canceled", "trialing"]
    key_expires_at: datetime | None
    cache_expires_at: float  # Unix timestamp for cache TTL

    @classmethod
    def from_validation_response(
        cls, response: AuthValidationResponse, cache_ttl_seconds: int
    ) -> "CachedAuthInfo":
        """Create cached info from validation response."""
        import time

        return cls(
            tenant_id=response.tenant.id,
            tenant_name=response.tenant.name,
            tenant_slug=response.tenant.slug,
            scope=response.api_key.scope,
            subscription_status=response.tenant.subscription_status,
            key_expires_at=response.api_key.expires_at,
            cache_expires_at=time.time() + cache_ttl_seconds,
        )

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        import time

        return time.time() > self.cache_expires_at
