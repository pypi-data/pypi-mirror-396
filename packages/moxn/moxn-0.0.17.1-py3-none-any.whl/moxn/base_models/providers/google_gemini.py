"""Google Gemini provider adapter implementation."""

from itertools import chain
from typing import Sequence

from moxn.base_models.blocks.context import MessageContext
from moxn.base_models.blocks.tool import ToolCall, ToolResult
from moxn.base_models.blocks.variable import TextVariable
from moxn.base_models.content_block import ContentBlock, TextContent
from moxn.base_models.providers.base import ProviderAdapter
from moxn.base_models.providers.utils import convert_blocks_to_document
from moxn.base_models.reducers.reducer_document import (
    reduce_document_blocks,
    shape_google_content_blocks,
)
from moxn.base_models.reducers.reducer_inline_variable import (
    reduce_inline_variable_blocks,
)
from moxn.types.content import MessageRole, Provider
from moxn.types.type_aliases.google import (
    GoogleContent,
    GoogleContentBlock,
    GoogleFunctionCall,
    GoogleFunctionResponse,
    GoogleMessagesParam,
    GooglePart,
    GoogleSystemContentBlock,
)


class AdapterGoogleGeminiSystem(
    ProviderAdapter[
        TextContent | TextVariable,
        GoogleSystemContentBlock,
        GoogleMessagesParam,
    ]
):
    """Adapter for Google Gemini System messages."""

    PROVIDER = Provider.GOOGLE_GEMINI

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[TextContent | TextVariable]],
        context: MessageContext,
    ) -> Sequence[Sequence[GoogleSystemContentBlock]]:
        """Convert blocks to Google Gemini-specific content document."""
        return convert_blocks_to_document(blocks, Provider.GOOGLE_GEMINI, context)

    @classmethod
    def to_provider_content_blocks(
        cls,
        blocks: Sequence[Sequence[TextContent | TextVariable]],
        context: MessageContext,
    ) -> Sequence[GoogleSystemContentBlock]:
        """Convert blocks to Google Gemini-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        document_with_merged_inline_variables = reduce_inline_variable_blocks(
            Provider.GOOGLE_GEMINI, blocks, document, MessageRole.SYSTEM
        )
        return reduce_document_blocks(
            Provider.GOOGLE_GEMINI,
            MessageRole.SYSTEM,
            document_with_merged_inline_variables,
        )

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[TextContent | TextVariable]],
        context: MessageContext,
    ) -> Sequence[GoogleMessagesParam]:
        """Convert blocks to Google Gemini-specific message parameter."""
        content_blocks = cls.to_provider_content_blocks(blocks, context)
        system_instruction = shape_google_content_blocks(
            content_blocks, role=MessageRole.SYSTEM
        )
        return [
            GoogleMessagesParam(
                system_instruction=system_instruction,
            )
        ]


class AdapterGoogleGeminiUser(
    ProviderAdapter[
        ContentBlock,
        GoogleContentBlock,
        GoogleMessagesParam,
    ]
):
    """Adapter for Google Gemini User messages."""

    PROVIDER = Provider.GOOGLE_GEMINI

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[Sequence[GoogleContentBlock]]:
        """Convert blocks to Google Gemini-specific content document."""
        return convert_blocks_to_document(blocks, Provider.GOOGLE_GEMINI, context)

    @classmethod
    def to_provider_content_blocks(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[GoogleContentBlock]:
        """Convert blocks to Google Gemini-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        document_with_merged_inline_variables = reduce_inline_variable_blocks(
            Provider.GOOGLE_GEMINI, blocks, document, MessageRole.USER
        )
        return reduce_document_blocks(
            Provider.GOOGLE_GEMINI,
            MessageRole.USER,
            document_with_merged_inline_variables,
        )

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[GoogleMessagesParam]:
        """Convert blocks to Google Gemini-specific message parameter."""
        content_blocks = cls.to_provider_content_blocks(blocks, context)
        shaped_blocks = shape_google_content_blocks(
            content_blocks, role=MessageRole.USER
        )
        return [
            GoogleMessagesParam(
                content=shaped_blocks,
            )
        ]


class AdapterGoogleGeminiModel(
    ProviderAdapter[
        ContentBlock,
        GoogleContentBlock,
        GoogleMessagesParam,
    ]
):
    """Adapter for Google Gemini Model messages."""

    PROVIDER = Provider.GOOGLE_GEMINI

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[Sequence[GoogleContentBlock]]:
        """Convert blocks to Google Gemini-specific content document."""
        return convert_blocks_to_document(blocks, Provider.GOOGLE_GEMINI, context)

    @classmethod
    def to_provider_content_blocks(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[GoogleContentBlock]:
        """Convert blocks to Google Gemini-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        document_with_merged_inline_variables = reduce_inline_variable_blocks(
            Provider.GOOGLE_GEMINI, blocks, document, MessageRole.MODEL
        )
        return reduce_document_blocks(
            Provider.GOOGLE_GEMINI,
            MessageRole.MODEL,
            document_with_merged_inline_variables,
        )

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[GoogleMessagesParam]:
        """Convert blocks to Google Gemini-specific message parameter."""
        content_blocks = cls.to_provider_content_blocks(blocks, context)
        shaped_blocks = shape_google_content_blocks(
            content_blocks, role=MessageRole.MODEL
        )
        return [
            GoogleMessagesParam(
                content=shaped_blocks,
            )
        ]


class AdapterGoogleGeminiToolCall(
    ProviderAdapter[
        ToolCall,
        GoogleFunctionCall,
        GoogleMessagesParam,
    ]
):
    """Adapter for Google Gemini Tool Call messages."""

    PROVIDER = Provider.GOOGLE_GEMINI

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ToolCall]],
        context: MessageContext,
    ) -> Sequence[Sequence[GoogleFunctionCall]]:
        """Convert blocks to Google Gemini-specific content document."""
        document = [
            [
                block.to_provider_content_block(Provider.GOOGLE_GEMINI, context)
                for block in block_group
            ]
            for block_group in blocks
        ]
        return document

    @classmethod
    def to_provider_content_blocks(
        cls,
        blocks: Sequence[Sequence[ToolCall]],
        context: MessageContext,
    ) -> Sequence[GoogleFunctionCall]:
        """Convert blocks to Google Gemini-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        content = reduce_document_blocks(
            Provider.GOOGLE_GEMINI,
            MessageRole.TOOL_CALL,
            document,
        )
        return content

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ToolCall]],
        context: MessageContext,
    ) -> Sequence[GoogleMessagesParam]:
        """Convert blocks to Google Gemini-specific message parameter."""
        content_blocks = cls.to_provider_content_blocks(blocks, context)
        content = GoogleContent(
            role="model",
            parts=[
                GooglePart.from_function_call(
                    name=function_call.name or "",
                    args=function_call.args or {},
                )
                for function_call in content_blocks
            ],
        )
        return [
            GoogleMessagesParam(
                content=[content],
            )
        ]


class AdapterGoogleGeminiToolResult(
    ProviderAdapter[
        ToolResult,
        GoogleFunctionResponse,
        GoogleMessagesParam,
    ]
):
    """Adapter for Google Gemini Tool Result messages."""

    PROVIDER = Provider.GOOGLE_GEMINI

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ToolResult]],
        context: MessageContext,
    ) -> Sequence[Sequence[GoogleFunctionResponse]]:
        """Convert blocks to Google Gemini-specific content document."""
        document = [
            [
                block.to_provider_content_block(Provider.GOOGLE_GEMINI, context)
                for block in block_group
            ]
            for block_group in blocks
        ]
        return document

    @classmethod
    def to_provider_content_blocks(
        cls,
        blocks: Sequence[Sequence[ToolResult]],
        context: MessageContext,
    ) -> Sequence[GoogleFunctionResponse]:
        """Convert blocks to Google Gemini-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        return list(chain.from_iterable(document))

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ToolResult]],
        context: MessageContext,
    ) -> Sequence[GoogleMessagesParam]:
        """Convert blocks to Google Gemini-specific message parameter."""
        content_blocks = cls.to_provider_content_blocks(blocks, context)
        content = GoogleContent(
            role="user",
            parts=[
                GooglePart.from_function_response(
                    name=function_response.name or "",
                    response=function_response.response or {},
                )
                for function_response in content_blocks
            ],
        )
        return [
            GoogleMessagesParam(
                content=[content],
            )
        ]
