from __future__ import annotations

import base64
from typing import Annotated

import httpx

# Third‑party provider SDK types
from pydantic import Field, TypeAdapter

from moxn.base_models.blocks.base import ToProviderContentBlockMixin
from moxn.base_models.blocks.context import MessageContext
from moxn.types.blocks.image import (
    MediaDataImageFormat,
    MediaImageFromBase64Model,
    MediaImageFromBytesModel,
    MediaImageFromGoogleFileModel,
    MediaImageFromGoogleFileReferenceModel,
    MediaImageFromLocalFileModel,
    MediaImageFromURLModel,
)
from moxn.types.type_aliases.anthropic import (
    AnthropicBase64ImageSourceParam,
    AnthropicImageBlockParam,
    AnthropicURLImageSourceParam,
)
from moxn.types.type_aliases.google import (
    GoogleFile,
    GooglePart,
)
from moxn.types.type_aliases.openai_chat import (
    OpenAIChatCompletionContentPartImageParam,
    OpenAIChatImageURL,
)
from moxn.types.type_aliases.openai_responses import (
    OpenAIResponsesInputImageParam,
)


class MediaImageFromBase64(MediaImageFromBase64Model, ToProviderContentBlockMixin):
    # ---------- provider adapters ----------
    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicImageBlockParam:
        return AnthropicImageBlockParam(
            type="image",
            source=AnthropicBase64ImageSourceParam(
                type="base64", media_type=self.media_type, data=self.base64
            ),
        )

    def _to_openai_chat_content_block(
        self, context: MessageContext
    ) -> OpenAIChatCompletionContentPartImageParam:
        data_uri = f"data:{self.media_type};base64,{self.base64}"
        return OpenAIChatCompletionContentPartImageParam(
            type="image_url", image_url=OpenAIChatImageURL(url=data_uri)
        )

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputImageParam:
        data_uri = f"data:{self.media_type};base64,{self.base64}"
        return OpenAIResponsesInputImageParam(
            type="input_image", image_url=data_uri, detail="auto"
        )

    def _to_google_gemini_content_block(self, context: MessageContext) -> GooglePart:
        return GooglePart.from_bytes(
            data=base64.b64decode(self.base64), mime_type=self.media_type
        )

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        return GooglePart.from_bytes(
            data=base64.b64decode(self.base64), mime_type=self.media_type
        )


class MediaImageFromBytes(MediaImageFromBytesModel, ToProviderContentBlockMixin):
    """
    Image provided as raw bytes.
    """

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicImageBlockParam:
        base64_data = image_to_base64(self)
        return AnthropicImageBlockParam(
            type="image",
            source=AnthropicBase64ImageSourceParam(
                type="base64", media_type=self.media_type, data=base64_data
            ),
        )

    def _to_openai_chat_content_block(
        self, context: MessageContext
    ) -> OpenAIChatCompletionContentPartImageParam:
        base64_data = image_to_base64(self)
        data_uri = f"data:{self.media_type};base64,{base64_data}"
        return OpenAIChatCompletionContentPartImageParam(
            type="image_url", image_url=OpenAIChatImageURL(url=data_uri)
        )

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputImageParam:
        base64_data = image_to_base64(self)
        data_uri = f"data:{self.media_type};base64,{base64_data}"
        return OpenAIResponsesInputImageParam(
            type="input_image", image_url=data_uri, detail="auto"
        )

    def _to_google_gemini_content_block(self, context: MessageContext) -> GooglePart:
        return GooglePart.from_bytes(data=self.bytes, mime_type=self.media_type)

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        return GooglePart.from_bytes(data=self.bytes, mime_type=self.media_type)


class MediaImageFromURL(MediaImageFromURLModel, ToProviderContentBlockMixin):
    """
    Image referenced by a URL.
    Note: For Google Vertex AI, public HTTP URLs are NOT supported for images.
    """

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicImageBlockParam:
        return AnthropicImageBlockParam(
            type="image",
            source=AnthropicURLImageSourceParam(type="url", url=self.url),
        )

    def _to_openai_chat_content_block(
        self, context: MessageContext
    ) -> OpenAIChatCompletionContentPartImageParam:
        return OpenAIChatCompletionContentPartImageParam(
            type="image_url", image_url=OpenAIChatImageURL(url=self.url)
        )

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputImageParam:
        return OpenAIResponsesInputImageParam(
            type="input_image", image_url=self.url, detail="auto"
        )

    def _to_google_gemini_content_block(self, context: MessageContext) -> GooglePart:
        bytes = url_to_bytes(self.url)
        return GooglePart.from_bytes(data=bytes, mime_type=self.media_type)

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        bytes = url_to_bytes(self.url)
        return GooglePart.from_bytes(data=bytes, mime_type=self.media_type)


class MediaImageFromLocalFile(
    MediaImageFromLocalFileModel, ToProviderContentBlockMixin
):
    """
    Image loaded from a local file path.
    """

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicImageBlockParam:
        base64_data = image_to_base64(self)
        return AnthropicImageBlockParam(
            type="image",
            source=AnthropicBase64ImageSourceParam(
                type="base64", media_type=self.media_type, data=base64_data
            ),
        )

    def _to_openai_chat_content_block(
        self, context: MessageContext
    ) -> OpenAIChatCompletionContentPartImageParam:
        base64_data = image_to_base64(self)
        data_uri = f"data:{self.media_type};base64,{base64_data}"
        return OpenAIChatCompletionContentPartImageParam(
            type="image_url", image_url=OpenAIChatImageURL(url=data_uri)
        )

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputImageParam:
        base64_data = image_to_base64(self)
        data_uri = f"data:{self.media_type};base64,{base64_data}"
        return OpenAIResponsesInputImageParam(
            type="input_image", image_url=data_uri, detail="auto"
        )

    def _to_google_gemini_content_block(self, context: MessageContext) -> GooglePart:
        bytes = image_to_bytes(self)
        return GooglePart.from_bytes(data=bytes, mime_type=self.media_type)

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        bytes = image_to_bytes(self)
        return GooglePart.from_bytes(data=bytes, mime_type=self.media_type)


class MediaImageFromGoogleFile(
    MediaImageFromGoogleFileModel, ToProviderContentBlockMixin
):
    """
    Image provided as a Google File object.
    Only supported by Google Gemini.
    """

    file: GoogleFile  # Override with specific type

    def _to_google_gemini_content_block(self, context: MessageContext) -> GoogleFile:
        return self.file

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicImageBlockParam:
        raise ValueError("Google File format not supported by Anthropic")

    def _to_openai_chat_content_block(
        self, context: MessageContext
    ) -> OpenAIChatCompletionContentPartImageParam:
        raise ValueError("Google File format not supported by OpenAI")

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputImageParam:
        raise ValueError("Google File format not supported by OpenAI Responses API")

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        raise ValueError("Google File format not directly supported by Vertex AI")


class MediaImageFromGoogleFileReference(
    MediaImageFromGoogleFileReferenceModel, ToProviderContentBlockMixin
):
    """
    Image referenced by a Google File URI.
    For Gemini Developer API: can be any URI
    For Vertex AI: must be a GCS URI (gs://)
    """

    def _to_google_gemini_content_block(self, context: MessageContext) -> GooglePart:
        if not self.uri.startswith("gs://"):
            raise ValueError(
                "Google Gemini requires a Cloud Storage (gs://) URI for images"
            )
        return GooglePart.from_uri(file_uri=self.uri, mime_type=self.media_type)

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        if not self.uri.startswith("gs://"):
            raise ValueError(
                "Vertex AI requires a Cloud Storage (gs://) URI for images"
            )
        return GooglePart.from_uri(file_uri=self.uri, mime_type=self.media_type)

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputImageParam:
        raise ValueError(
            "Google Cloud Storage URIs not supported by OpenAI Responses API"
        )

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicImageBlockParam:
        raise ValueError("Google File Reference format not supported by Anthropic")

    def _to_openai_chat_content_block(
        self, context: MessageContext
    ) -> OpenAIChatCompletionContentPartImageParam:
        raise ValueError("Google File Reference format not supported by OpenAI")


# --------------------------------------------------------------------------- #
# 3. Discriminated union
# --------------------------------------------------------------------------- #
_ImageContentFromSourceTypes = (
    MediaImageFromBase64
    | MediaImageFromBytes
    | MediaImageFromURL
    | MediaImageFromLocalFile
    | MediaImageFromGoogleFile
    | MediaImageFromGoogleFileReference
)
ImageContentFromSource = Annotated[
    _ImageContentFromSourceTypes,
    Field(discriminator="type"),
]

ImageContentFromSourceAdapter: TypeAdapter[_ImageContentFromSourceTypes] = TypeAdapter(
    _ImageContentFromSourceTypes
)


# --------------------------------------------------------------------------- #
# 4. Convenience helpers
# --------------------------------------------------------------------------- #
def url_to_bytes(url: str) -> bytes:
    """Convert a URL to bytes."""
    return httpx.get(url).content


def url_to_base64(url: str) -> str:
    """Convert a URL to base64 string."""
    return base64.b64encode(url_to_bytes(url)).decode("utf-8")


def image_to_base64(img: ImageContentFromSource) -> str:
    """Convert any ImageContent type to base64 string."""
    if hasattr(img, "type"):
        if img.type == MediaDataImageFormat.BASE64:
            return img.base64
        if img.type == MediaDataImageFormat.BYTES:
            return base64.b64encode(img.bytes).decode("utf-8")
        if img.type == MediaDataImageFormat.URL:
            return url_to_base64(img.url)
        if img.type == MediaDataImageFormat.LOCAL_FILE:
            return base64.b64encode(img.filepath.read_bytes()).decode("utf-8")
    raise ValueError(f"Unsupported media type: {getattr(img, 'type', 'unknown')}")


def image_to_bytes(img: ImageContentFromSource) -> bytes:
    """Convert any ImageContent type to bytes."""
    if hasattr(img, "type"):
        if img.type == MediaDataImageFormat.BASE64:
            return base64.b64decode(img.base64)
        if img.type == MediaDataImageFormat.BYTES:
            return img.bytes
        if img.type == MediaDataImageFormat.URL:
            return url_to_bytes(img.url)
        if img.type == MediaDataImageFormat.LOCAL_FILE:
            return img.filepath.read_bytes()
    raise ValueError(f"Unsupported media type: {getattr(img, 'type', 'unknown')}")
