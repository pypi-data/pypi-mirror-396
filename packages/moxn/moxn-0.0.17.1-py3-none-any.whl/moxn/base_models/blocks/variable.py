from __future__ import annotations

from typing import Annotated, Any, Literal, cast, overload

# Third-party provider SDK types
from anthropic.types import DocumentBlockParam, ImageBlockParam, TextBlockParam
from google.genai import types
from openai.types.chat import (
    ChatCompletionContentPartImageParam,
    ChatCompletionContentPartTextParam,
)
from openai.types.chat.chat_completion_content_part_param import File as OpenAIChatFile
from pydantic import Field, TypeAdapter

from moxn.types.type_aliases.openai_responses import (
    OpenAIResponsesContentBlock,
    OpenAIResponsesInputFileParam,
    OpenAIResponsesInputTextParam,
)
from moxn.base_models.blocks.base import ToProviderContentBlockMixin
from moxn.base_models.blocks.context import MessageContext
from moxn.base_models.blocks.text import (
    TextContent,
    ToProviderContentBlockMixinTextOnly,
)
from moxn.types.blocks.base import BlockType
from moxn.types.blocks.variable import (
    FileVariableModel,
    ImageVariableModel,
    TextVariableModel,
)
from moxn.types.content import Provider

# --------------------------------------------------------------------------- #
# 1. Text variable implementations
# --------------------------------------------------------------------------- #


class TextVariable(TextVariableModel, ToProviderContentBlockMixinTextOnly):
    # Override the to_provider_content_block method with more specific types
    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.ANTHROPIC], context: MessageContext
    ) -> TextBlockParam: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.OPENAI_CHAT], context: MessageContext
    ) -> ChatCompletionContentPartTextParam: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.OPENAI_RESPONSES], context: MessageContext
    ) -> OpenAIResponsesInputTextParam: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.GOOGLE_GEMINI], context: MessageContext
    ) -> types.Part: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.GOOGLE_VERTEX], context: MessageContext
    ) -> types.Part: ...

    # Implement the method (same as in parent class)
    def to_provider_content_block(self, provider: Provider, context: MessageContext):
        if provider == Provider.ANTHROPIC:
            return self._to_anthropic_content_block(context)
        elif provider == Provider.OPENAI_CHAT:
            return self._to_openai_chat_content_block(context)
        elif provider == Provider.OPENAI_RESPONSES:
            return self._to_openai_responses_content_block(context)
        elif provider == Provider.GOOGLE_GEMINI:
            return self._to_google_gemini_content_block(context)
        elif provider == Provider.GOOGLE_VERTEX:
            return self._to_google_vertex_content_block(context)
        else:
            raise ValueError("Unsupported provider")

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> TextBlockParam | Any:
        # Get value from context or fall back to default
        value = context.get_variable(self.name, self.variable_type, self.default_value)

        if value is None and self.required:
            raise ValueError(f"Missing required variable: {self.name}")

        # Check if it's already a ContentBlock or list of ContentBlocks
        if hasattr(value, "_to_anthropic_content_block"):
            # It's a ContentBlock - pass through directly
            return value._to_anthropic_content_block(context)
        elif isinstance(value, (list, tuple)) and all(
            hasattr(v, "_to_anthropic_content_block") for v in value
        ):
            # For lists, we need to return the list of converted blocks
            # This will be handled by the message converter
            return [v._to_anthropic_content_block(context) for v in value]
        else:
            # Use value or empty string for backward compatibility
            text_value = str(value) if value is not None else ""
            return TextContent(text=text_value)._to_anthropic_content_block(context)

    def _to_openai_chat_content_block(
        self, context: MessageContext
    ) -> ChatCompletionContentPartTextParam | Any:
        # Get value from context or fall back to default
        value = context.get_variable(self.name, self.variable_type, self.default_value)

        if value is None and self.required:
            raise ValueError(f"Missing required variable: {self.name}")

        # Check if it's already a ContentBlock or list of ContentBlocks
        if hasattr(value, "_to_openai_chat_content_block"):
            # It's a ContentBlock - pass through directly
            return value._to_openai_chat_content_block(context)
        elif isinstance(value, (list, tuple)) and all(
            hasattr(v, "_to_openai_chat_content_block") for v in value
        ):
            # For lists, we need to return the list of converted blocks
            return [v._to_openai_chat_content_block(context) for v in value]
        else:
            # Use value or empty string for backward compatibility
            text_value = str(value) if value is not None else ""
            return TextContent(text=text_value)._to_openai_chat_content_block(context)

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputTextParam | Any:
        # Get value from context or fall back to default
        value = context.get_variable(self.name, self.variable_type, self.default_value)

        if value is None and self.required:
            raise ValueError(f"Missing required variable: {self.name}")

        # Check if it's already a ContentBlock or list of ContentBlocks
        if hasattr(value, "_to_openai_responses_content_block"):
            # It's a ContentBlock - pass through directly
            return value._to_openai_responses_content_block(context)
        elif isinstance(value, (list, tuple)) and all(
            hasattr(v, "_to_openai_responses_content_block") for v in value
        ):
            # For lists, we need to return the list of converted blocks
            return [v._to_openai_responses_content_block(context) for v in value]
        else:
            # Use value or empty string for backward compatibility
            text_value = str(value) if value is not None else ""
            return TextContent(text=text_value)._to_openai_responses_content_block(
                context
            )

    def _to_google_gemini_content_block(
        self, context: MessageContext
    ) -> types.Part | Any:
        # Get value from context or fall back to default
        value = context.get_variable(self.name, self.variable_type, self.default_value)

        if value is None and self.required:
            raise ValueError(f"Missing required variable: {self.name}")

        # Check if it's already a ContentBlock or list of ContentBlocks
        if hasattr(value, "_to_google_gemini_content_block"):
            # It's a ContentBlock - pass through directly
            return value._to_google_gemini_content_block(context)
        elif isinstance(value, (list, tuple)) and all(
            hasattr(v, "_to_google_gemini_content_block") for v in value
        ):
            # For lists, we need to return the list of converted blocks
            return [v._to_google_gemini_content_block(context) for v in value]
        else:
            # Use value or empty string for backward compatibility
            text_value = str(value) if value is not None else ""
            return TextContent(text=text_value)._to_google_gemini_content_block(context)

    def _to_google_vertex_content_block(
        self, context: MessageContext
    ) -> types.Part | Any:
        # Get value from context or fall back to default
        value = context.get_variable(self.name, self.variable_type, self.default_value)

        if value is None and self.required:
            raise ValueError(f"Missing required variable: {self.name}")

        # Check if it's already a ContentBlock or list of ContentBlocks
        if hasattr(value, "_to_google_vertex_content_block"):
            # It's a ContentBlock - pass through directly
            return value._to_google_vertex_content_block(context)
        elif isinstance(value, (list, tuple)) and all(
            hasattr(v, "_to_google_vertex_content_block") for v in value
        ):
            # For lists, we need to return the list of converted blocks
            return [v._to_google_vertex_content_block(context) for v in value]
        else:
            # Use value or empty string for backward compatibility
            text_value = str(value) if value is not None else ""
            return TextContent(text=text_value)._to_google_vertex_content_block(context)


# --------------------------------------------------------------------------- #
# 4. Image variable implementations
# --------------------------------------------------------------------------- #
class ImageVariable(ImageVariableModel, ToProviderContentBlockMixin):
    """A variable that represents image content."""

    def _to_anthropic_content_block(self, context: MessageContext) -> ImageBlockParam:
        # Get image from context variables
        image = context.get_variable(self.name, self.variable_type)

        if image is None and self.required:
            raise ValueError(f"Missing required image variable: {self.name}")
        elif image is None:
            raise ValueError(f"Missing value for image variable: {self.name}")

        if not image.block_type == BlockType.IMAGE:
            raise TypeError(f"Variable {self.name} must be an ImageContentFromSource")

        return image._to_anthropic_content_block(context)

    def _to_openai_chat_content_block(
        self, context: MessageContext
    ) -> ChatCompletionContentPartImageParam:
        # Get image from context variables
        image = context.get_variable(self.name, self.variable_type)

        if image is None and self.required:
            raise ValueError(f"Missing required image variable: {self.name}")
        elif image is None:
            raise ValueError(f"Missing value for image variable: {self.name}")

        if not image.block_type == BlockType.IMAGE:
            raise TypeError(f"Variable {self.name} must be an ImageContentFromSource")

        return image._to_openai_chat_content_block(context)

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesContentBlock:
        # Get image from context variables
        image = context.get_variable(self.name, self.variable_type)

        if image is None and self.required:
            raise ValueError(f"Missing required image variable: {self.name}")
        elif image is None:
            raise ValueError(f"Missing value for image variable: {self.name}")

        if not image.block_type == BlockType.IMAGE:
            raise TypeError(f"Variable {self.name} must be an ImageContentFromSource")

        return image._to_openai_responses_content_block(context)

    def _to_google_gemini_content_block(
        self, context: MessageContext
    ) -> types.Part | types.File:
        # Get image from context variables
        image = context.get_variable(self.name, self.variable_type)

        if image is None and self.required:
            raise ValueError(f"Missing required image variable: {self.name}")
        elif image is None:
            raise ValueError(f"Missing value for image variable: {self.name}")

        if not image.block_type == BlockType.IMAGE:
            raise TypeError(f"Variable {self.name} must be an ImageContentFromSource")

        return image._to_google_gemini_content_block(context)

    def _to_google_vertex_content_block(self, context: MessageContext) -> types.Part:
        # Get image from context variables
        image = context.get_variable(self.name, self.variable_type)

        if image is None and self.required:
            raise ValueError(f"Missing required image variable: {self.name}")
        elif image is None:
            raise ValueError(f"Missing value for image variable: {self.name}")

        if not image.block_type == BlockType.IMAGE:
            raise TypeError(f"Variable {self.name} must be an ImageContentFromSource")

        return image._to_google_vertex_content_block(context)


# --------------------------------------------------------------------------- #
# 5. File variable implementations
# --------------------------------------------------------------------------- #
class FileVariable(FileVariableModel, ToProviderContentBlockMixin):
    """A variable that represents document content (PDF)."""

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> DocumentBlockParam:
        # Get document from context variables
        pdf = context.get_variable(self.name, self.variable_type)

        if pdf is None and self.required:
            raise ValueError(f"Missing required document variable: {self.name}")
        elif pdf is None:
            raise ValueError(f"Missing value for document variable: {self.name}")

        if not pdf.block_type == BlockType.FILE:
            raise TypeError(f"Variable {self.name} must be a PDFContentFromSource")

        return cast(DocumentBlockParam, pdf._to_anthropic_content_block(context))

    def _to_openai_chat_content_block(self, context: MessageContext) -> OpenAIChatFile:
        # Get document from context variables
        pdf = context.get_variable(self.name, self.variable_type)

        if pdf is None and self.required:
            raise ValueError(f"Missing required document variable: {self.name}")
        elif pdf is None:
            raise ValueError(f"Missing value for document variable: {self.name}")

        if not pdf.block_type == BlockType.FILE:
            raise TypeError(f"Variable {self.name} must be a PDFContentFromSource")

        return cast(OpenAIChatFile, pdf._to_openai_chat_content_block(context))

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputFileParam:
        # Get document from context variables
        pdf = context.get_variable(self.name, self.variable_type)

        if pdf is None and self.required:
            raise ValueError(f"Missing required document variable: {self.name}")
        elif pdf is None:
            raise ValueError(f"Missing value for document variable: {self.name}")

        if not pdf.block_type == BlockType.FILE:
            raise TypeError(f"Variable {self.name} must be a PDFContentFromSource")

        return cast(
            OpenAIResponsesInputFileParam,
            pdf._to_openai_responses_content_block(context),
        )

    def _to_google_gemini_content_block(
        self, context: MessageContext
    ) -> types.Part | types.File:
        # Get document from context variables
        pdf = context.get_variable(self.name, self.variable_type)

        if pdf is None and self.required:
            raise ValueError(f"Missing required document variable: {self.name}")
        elif pdf is None:
            raise ValueError(f"Missing value for document variable: {self.name}")

        if not pdf.block_type == BlockType.FILE:
            raise TypeError(f"Variable {self.name} must be a PDFContentFromSource")

        return pdf._to_google_gemini_content_block(context)

    def _to_google_vertex_content_block(self, context: MessageContext) -> types.Part:
        # Get document from context variables
        pdf = context.get_variable(self.name, self.variable_type)

        if pdf is None and self.required:
            raise ValueError(f"Missing required document variable: {self.name}")
        elif pdf is None:
            raise ValueError(f"Missing value for document variable: {self.name}")

        if not pdf.block_type == BlockType.FILE:
            raise TypeError(f"Variable {self.name} must be a PDFContentFromSource")

        return pdf._to_google_vertex_content_block(context)


# --------------------------------------------------------------------------- #
# 6. Discriminated union
# --------------------------------------------------------------------------- #
_VariableTypes = TextVariable | ImageVariable | FileVariable

Variable = Annotated[
    _VariableTypes,
    Field(discriminator="variable_type"),
]

VariableAdapter: TypeAdapter[_VariableTypes] = TypeAdapter(_VariableTypes)
