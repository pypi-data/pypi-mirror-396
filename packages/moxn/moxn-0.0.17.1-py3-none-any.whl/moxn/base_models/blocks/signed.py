from datetime import datetime, timedelta, timezone
from typing import Any

from pydantic import model_validator

from moxn.base_models.blocks.base import ToProviderContentBlockMixin
from moxn.base_models.blocks.context import MessageContext
from moxn.base_models.blocks.file import MediaDataPDFFromURL
from moxn.base_models.blocks.image import (
    MediaImageFromURL,
)
from moxn.types.blocks.signed import (
    SignedURLContentModel,
    SignedURLImageContentModel,
    SignedURLPDFContentModel,
)
from moxn.types.type_aliases.anthropic import (
    AnthropicFileBlockParam,
    AnthropicImageBlockParam,
)
from moxn.types.type_aliases.google import GooglePart
from moxn.types.type_aliases.openai_chat import (
    OpenAIChatCompletionContentPartImageParam,
    OpenAIChatFile,
)
from moxn.types.type_aliases.openai_responses import (
    OpenAIResponsesInputFileParam,
    OpenAIResponsesInputImageParam,
)


class SignedURLContent(SignedURLContentModel, ToProviderContentBlockMixin):
    @model_validator(mode="wrap")
    @classmethod
    def _create_appropriate_subclass(cls, value: Any, handler):
        """Create appropriate subclass based on media_type.

        This validator inspects the media_type field and returns the correct
        subclass instance (SignedURLImageContent or SignedURLPDFContent) to
        maintain type distinction for provider conversion and isinstance checks.

        IMPORTANT: Only runs on base SignedURLContent class, not on subclasses,
        to prevent infinite recursion.
        """
        # Only run subclass creation logic when validating the base class
        # If we're validating a subclass, skip this to avoid infinite recursion
        if cls is not SignedURLContent:
            return handler(value)

        # Only process dicts (raw API responses)
        if isinstance(value, dict):
            # Check both snake_case and camelCase variants
            media_type = value.get("media_type") or value.get("mediaType")

            if media_type:
                # Import here to avoid circular imports
                if media_type.startswith("image/"):
                    # Return image subclass instance
                    return SignedURLImageContent.model_validate(value)
                elif media_type == "application/pdf":
                    # Return PDF subclass instance
                    return SignedURLPDFContent.model_validate(value)

        # Default handling for non-dict or no media_type
        return handler(value)

    @property
    def url(self) -> str:
        if self.signed_url:
            return self.signed_url
        raise ValueError("URL not set")

    def should_refresh(self) -> bool:
        if self.expiration is None:
            return True

        # Ensure expiration is timezone-aware
        expiration = self._ensure_timezone_aware(self.expiration)
        now = datetime.now(timezone.utc)

        return expiration < now + timedelta(seconds=self.buffer_seconds)

    def _ensure_timezone_aware(self, dt: datetime) -> datetime:
        """Ensure datetime is timezone-aware, converting to UTC if it's naive"""
        if dt.tzinfo is None:
            # Convert naive datetime to UTC
            return dt.replace(tzinfo=timezone.utc)
        return dt


class SignedURLImageContent(SignedURLImageContentModel, SignedURLContent):
    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicImageBlockParam:
        return MediaImageFromURL(
            url=self.url,
            mediaType=self.media_type,
        )._to_anthropic_content_block(context)

    def _to_openai_chat_content_block(
        self, context: MessageContext
    ) -> OpenAIChatCompletionContentPartImageParam:
        return MediaImageFromURL(
            url=self.url,
            mediaType=self.media_type,
        )._to_openai_chat_content_block(context)

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputImageParam:
        return MediaImageFromURL(
            url=self.url,
            mediaType=self.media_type,
        )._to_openai_responses_content_block(context)

    def _to_google_gemini_content_block(self, context: MessageContext) -> GooglePart:
        return MediaImageFromURL(
            url=self.url,
            mediaType=self.media_type,
        )._to_google_gemini_content_block(context)

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        return MediaImageFromURL(
            url=self.url,
            mediaType=self.media_type,
        )._to_google_vertex_content_block(context)


class SignedURLPDFContent(SignedURLPDFContentModel, SignedURLContent):
    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicFileBlockParam:
        return MediaDataPDFFromURL(
            url=self.url,
            mediaType=self.media_type,
        )._to_anthropic_content_block(context)

    def _to_openai_chat_content_block(self, context: MessageContext) -> OpenAIChatFile:
        return MediaDataPDFFromURL(
            url=self.url,
            mediaType=self.media_type,
            filename=self.filename,
        )._to_openai_chat_content_block(context)

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputFileParam:
        return MediaDataPDFFromURL(
            url=self.url,
            mediaType=self.media_type,
            filename=self.filename,
        )._to_openai_responses_content_block(context)

    def _to_google_gemini_content_block(self, context: MessageContext) -> GooglePart:
        return MediaDataPDFFromURL(
            url=self.url,
            mediaType=self.media_type,
        )._to_google_gemini_content_block(context)

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        return MediaDataPDFFromURL(
            url=self.url,
            mediaType=self.media_type,
        )._to_google_vertex_content_block(context)
