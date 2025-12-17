import base64
from typing import Annotated

import httpx
from moxn.base_models.blocks.base import ToProviderContentBlockMixin
from moxn.base_models.blocks.context import MessageContext
from moxn.types.blocks.file import (
    MediaDataPDFFormat,
    MediaDataPDFFromBase64Model,
    MediaDataPDFFromBytesModel,
    MediaDataPDFFromGoogleFileModel,
    MediaDataPDFFromGoogleFileReferenceModel,
    MediaDataPDFFromLocalFileModel,
    MediaDataPDFFromOpenAIChatFileReferenceModel,
    MediaDataPDFFromURLModel,
)
from moxn.types.type_aliases.anthropic import (
    AnthropicBase64PDFSourceParam,
    AnthropicFileBlockParam,
    AnthropicURLPDFSourceParam,
)
from moxn.types.type_aliases.google import (
    GoogleFile,
    GooglePart,
)
from moxn.types.type_aliases.openai_chat import (
    OpenAIChatFile,
    OpenAIChatFileFile,
)
from moxn.types.type_aliases.openai_responses import (
    OpenAIResponsesInputFileParam,
)
from pydantic import Field, TypeAdapter

# Class names define how we recieve the data
# Utilities convert to the correct format for the provider
# Type is used as a discriminator to present single interface


class MediaDataPDFFromBase64(MediaDataPDFFromBase64Model, ToProviderContentBlockMixin):
    """
    PDF of mime type pdf encoded in base64.
    """

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicFileBlockParam:
        return AnthropicFileBlockParam(
            source=AnthropicBase64PDFSourceParam(
                type="base64",
                media_type=self.media_type,
                data=self.base64,
            ),
            type="document",
        )

    def _to_openai_chat_content_block(self, context: MessageContext) -> OpenAIChatFile:
        return OpenAIChatFile(
            file=OpenAIChatFileFile(
                file_data=self.base64,
                filename=self.filename,
            ),
            type="file",
        )

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputFileParam:
        return OpenAIResponsesInputFileParam(
            type="input_file",
            file_data=self.base64,
            filename=self.filename,
        )

    def _to_google_gemini_content_block(self, context: MessageContext) -> GooglePart:
        return GooglePart.from_bytes(
            data=pdf_to_bytes(self),
            mime_type=self.media_type,
        )

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        return GooglePart.from_bytes(
            data=pdf_to_bytes(self),
            mime_type=self.media_type,
        )


class MediaDataPDFFromBytes(MediaDataPDFFromBytesModel, ToProviderContentBlockMixin):
    """
    PDF of mime type pdf encoded in bytes.
    """

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicFileBlockParam:
        base64_data = pdf_to_base64(self)
        return AnthropicFileBlockParam(
            source=AnthropicBase64PDFSourceParam(
                type="base64",
                media_type=self.media_type,
                data=base64_data,
            ),
            type="document",
        )

    def _to_openai_chat_content_block(self, context: MessageContext) -> OpenAIChatFile:
        base64_data = pdf_to_base64(self)
        return OpenAIChatFile(
            file=OpenAIChatFileFile(
                file_data=base64_data,
                filename=self.filename,
            ),
            type="file",
        )

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputFileParam:
        return OpenAIResponsesInputFileParam(
            type="input_file",
            file_data=pdf_to_base64(self),
            filename=self.filename,
        )

    def _to_google_gemini_content_block(self, context: MessageContext) -> GooglePart:
        return GooglePart.from_bytes(
            data=self.bytes,
            mime_type=self.media_type,
        )

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        return GooglePart.from_bytes(
            data=self.bytes,
            mime_type=self.media_type,
        )


class MediaDataPDFFromURL(MediaDataPDFFromURLModel, ToProviderContentBlockMixin):
    """
    PDF of mime type pdf encoded in url. URL must be a valid pdf url accessible via http/https.
    Note: For Google Vertex AI, public HTTP URLs are not supported - use GCS URIs instead.
    """

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicFileBlockParam:
        return AnthropicFileBlockParam(
            source=AnthropicURLPDFSourceParam(
                type="url",
                url=self.url,
            ),
            type="document",
        )

    def _to_openai_chat_content_block(self, context: MessageContext) -> OpenAIChatFile:
        return OpenAIChatFile(
            file=OpenAIChatFileFile(
                file_data=url_to_base64(self.url),
                filename=self.filename,
            ),
            type="file",
        )

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputFileParam:
        return OpenAIResponsesInputFileParam(
            type="input_file",
            file_data=url_to_base64(self.url),
            filename=self.filename,
        )

    def _to_google_gemini_content_block(self, context: MessageContext) -> GooglePart:
        # Gemini Developer API does support public URLs - must use inline bytes
        # This is less efficient but provides compatibility
        return GooglePart.from_bytes(
            data=url_to_bytes(self.url),
            mime_type=self.media_type,
        )

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        # Vertex AI doesn't support public URLs - must use inline bytes
        # This is less efficient but provides compatibility
        return GooglePart.from_bytes(
            data=url_to_bytes(self.url),
            mime_type=self.media_type,
        )


class MediaDataPDFFromOpenAIChatFileReference(
    MediaDataPDFFromOpenAIChatFileReferenceModel, ToProviderContentBlockMixin
):
    """
    PDF of mime type pdf encoded in OpenAI File ID Reference.
    """

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicFileBlockParam:
        raise ValueError("OpenAI File Reference format not supported by Anthropic")

    def _to_openai_chat_content_block(self, context: MessageContext) -> OpenAIChatFile:
        return OpenAIChatFile(
            file=OpenAIChatFileFile(
                file_id=self.file_id,
            ),
            type="file",
        )

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputFileParam:
        return OpenAIResponsesInputFileParam(
            type="input_file",
            file_id=self.file_id,
        )

    def _to_google_gemini_content_block(self, context: MessageContext) -> GooglePart:
        raise ValueError("OpenAI File Reference format not supported by Gemini")

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        raise ValueError("OpenAI File Reference format not supported by Vertex AI")


class MediaDataPDFFromGoogleFile(
    MediaDataPDFFromGoogleFileModel, ToProviderContentBlockMixin
):
    """
    PDF of mime type pdf encoded in Google File.
    """

    file: GoogleFile  # Override with specific type

    def _to_google_gemini_content_block(self, context: MessageContext) -> GoogleFile:
        return self.file

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicFileBlockParam:
        raise ValueError("Google File format not supported by Anthropic")

    def _to_openai_chat_content_block(self, context: MessageContext) -> OpenAIChatFile:
        raise ValueError("Google File format not supported by OpenAI")

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputFileParam:
        raise ValueError("Google File format not supported by OpenAI Responses API")

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        raise ValueError("Google File format not directly supported by Vertex AI")


class MediaDataPDFFromGoogleFileReference(
    MediaDataPDFFromGoogleFileReferenceModel, ToProviderContentBlockMixin
):
    """
    PDF of mime type pdf encoded in Google File ID Reference.
    For Gemini Developer API: can be a types.File ID from client.files.upload()
    For Vertex AI: must be a GCS URI (gs://) with specified MIME type
    """

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicFileBlockParam:
        raise ValueError("Google File Reference format not supported by Anthropic")

    def _to_openai_chat_content_block(self, context: MessageContext) -> OpenAIChatFile:
        raise ValueError("Google File Reference format not supported by OpenAI")

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputFileParam:
        raise ValueError("Google File format not supported by OpenAI Responses API")

    def _to_google_gemini_content_block(self, context: MessageContext) -> GoogleFile:  # type: ignore
        # For Gemini Developer API, this could be a File ID from Files API
        # Or it could be a GCS URI
        return GoogleFile(
            uri=self.uri,
        )

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        # Vertex AI only supports GCS URIs for remote files
        raise ValueError(
            "Vertex AI only supports GCS URIs (gs://) for file references. "
            "Public HTTP URLs are not supported."
        )


class MediaDataPDFFromLocalFile(
    MediaDataPDFFromLocalFileModel, ToProviderContentBlockMixin
):
    """
    PDF of mime type pdf encoded in local file.
    """

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicFileBlockParam:
        return AnthropicFileBlockParam(
            source=AnthropicBase64PDFSourceParam(
                type="base64",
                data=base64.b64encode(self.filepath.read_bytes()).decode("utf-8"),
                media_type=self.media_type,
            ),
            type="document",
        )

    def _to_openai_chat_content_block(self, context: MessageContext) -> OpenAIChatFile:
        return OpenAIChatFile(
            file=OpenAIChatFileFile(
                file_data=base64.b64encode(self.filepath.read_bytes()).decode("utf-8"),
                filename=self.filename,
            ),
            type="file",
        )

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputFileParam:
        return OpenAIResponsesInputFileParam(
            type="input_file",
            file_data=pdf_to_base64(self),
            filename=self.filename,
        )

    def _to_google_gemini_content_block(self, context: MessageContext) -> GooglePart:
        return GooglePart.from_bytes(
            data=self.filepath.read_bytes(),
            mime_type=self.media_type,
        )

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        return GooglePart.from_bytes(
            data=self.filepath.read_bytes(),
            mime_type=self.media_type,
        )


_PDFContentFromSourceTypes = (
    MediaDataPDFFromBase64
    | MediaDataPDFFromBytes
    | MediaDataPDFFromLocalFile
    | MediaDataPDFFromGoogleFile
    | MediaDataPDFFromGoogleFileReference
    | MediaDataPDFFromOpenAIChatFileReference
    | MediaDataPDFFromURL
)

PDFContentFromSource = Annotated[
    _PDFContentFromSourceTypes, Field(discriminator="type")
]

PDFContentFromSourceAdapter: TypeAdapter[_PDFContentFromSourceTypes] = TypeAdapter(
    _PDFContentFromSourceTypes
)


def pdf_to_base64(media_data: PDFContentFromSource) -> str:
    """Convert any PDFContent type to base64 string."""
    if media_data.type == MediaDataPDFFormat.BASE64:
        return media_data.base64
    elif media_data.type == MediaDataPDFFormat.BYTES:
        return base64.b64encode(media_data.bytes).decode("utf-8")
    elif media_data.type == MediaDataPDFFormat.URL:
        return base64.b64encode(httpx.get(str(media_data.url)).content).decode("utf-8")
    elif media_data.type == MediaDataPDFFormat.LOCAL_FILE:
        return base64.b64encode(media_data.filepath.read_bytes()).decode("utf-8")
    else:
        raise ValueError(f"Unsupported media type: {media_data.type}")


def pdf_to_bytes(media_data: PDFContentFromSource) -> bytes:
    """Convert any ImageData type to bytes."""
    if media_data.type == MediaDataPDFFormat.BASE64:
        return base64.b64decode(media_data.base64)
    elif media_data.type == MediaDataPDFFormat.BYTES:
        return media_data.bytes
    elif media_data.type == MediaDataPDFFormat.URL:
        return httpx.get(str(media_data.url)).content
    elif media_data.type == MediaDataPDFFormat.LOCAL_FILE:
        return media_data.filepath.read_bytes()
    else:
        raise ValueError(f"Unsupported media type: {media_data.type}")


def url_to_bytes(url: str) -> bytes:
    """Convert a link to bytes."""
    return httpx.get(url).content


def url_to_base64(url: str) -> str:
    """Convert a link to base64."""
    return base64.b64encode(url_to_bytes(url)).decode("utf-8")
