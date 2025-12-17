"""Anthropic provider adapter implementation."""

from itertools import chain
from typing import Sequence

from moxn.base_models.blocks.context import MessageContext
from moxn.base_models.blocks.tool import ToolCall, ToolResult
from moxn.base_models.blocks.variable import TextVariable
from moxn.base_models.content_block import ContentBlock, TextContent
from moxn.base_models.providers.base import ProviderAdapter
from moxn.base_models.providers.utils import convert_blocks_to_document
from moxn.base_models.reducers.reducer_document import reduce_document_blocks
from moxn.base_models.reducers.reducer_inline_variable import (
    reduce_inline_variable_blocks,
)
from moxn.types.content import MessageRole, Provider
from moxn.types.type_aliases.anthropic import (
    AnthropicContentBlockParam,
    AnthropicMessageParam,
    AnthropicTextBlockParam,
    AnthropicToolResultBlockParam,
    AnthropicToolUseBlockParam,
)


class AdapterAnthropicSystem(
    ProviderAdapter[
        TextContent | TextVariable,
        AnthropicTextBlockParam,
        AnthropicTextBlockParam,
    ]
):
    """Adapter for Anthropic API."""

    PROVIDER = Provider.ANTHROPIC

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[TextContent | TextVariable]],
        context: MessageContext,
    ) -> Sequence[Sequence[AnthropicTextBlockParam]]:
        """Convert blocks to Anthropic-specific content document."""
        return convert_blocks_to_document(blocks, Provider.ANTHROPIC, context)

    @classmethod
    def to_provider_content_blocks(
        cls,
        blocks: Sequence[Sequence[TextContent | TextVariable]],
        context: MessageContext,
    ) -> Sequence[AnthropicTextBlockParam]:
        """Convert blocks to Anthropic-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        document_with_merged_inline_variables = reduce_inline_variable_blocks(
            Provider.ANTHROPIC, blocks, document, MessageRole.SYSTEM
        )
        return reduce_document_blocks(
            Provider.ANTHROPIC,
            MessageRole.SYSTEM,
            document_with_merged_inline_variables,
        )

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[TextContent | TextVariable]],
        context: MessageContext,
    ) -> Sequence[AnthropicTextBlockParam]:
        """Convert blocks to Anthropic-specific message parameter."""
        return cls.to_provider_content_blocks(blocks, context)


class AdapterAnthropicUser(
    ProviderAdapter[ContentBlock, AnthropicContentBlockParam, AnthropicMessageParam]
):
    """Adapter for Anthropic API."""

    PROVIDER = Provider.ANTHROPIC

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[Sequence[AnthropicContentBlockParam]]:
        """Convert blocks to Anthropic-specific content document."""
        return convert_blocks_to_document(blocks, Provider.ANTHROPIC, context)

    @classmethod
    def to_provider_content_blocks(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[AnthropicContentBlockParam]:
        """Convert blocks to Anthropic-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        document_with_merged_inline_variables = reduce_inline_variable_blocks(
            Provider.ANTHROPIC, blocks, document, MessageRole.USER
        )
        return reduce_document_blocks(
            Provider.ANTHROPIC,
            MessageRole.USER,
            document_with_merged_inline_variables,
        )

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[AnthropicMessageParam]:
        """Convert blocks to Anthropic-specific message parameter."""
        return [
            AnthropicMessageParam(
                content=cls.to_provider_content_blocks(blocks, context),
                role=MessageRole.USER.value,
            )
        ]


class AdapterAnthropicAssistant(
    ProviderAdapter[ContentBlock, AnthropicContentBlockParam, AnthropicMessageParam]
):
    """Adapter for Anthropic API."""

    PROVIDER = Provider.ANTHROPIC

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[Sequence[AnthropicContentBlockParam]]:
        """Convert blocks to Anthropic-specific content document."""
        return convert_blocks_to_document(blocks, Provider.ANTHROPIC, context)

    @classmethod
    def to_provider_content_blocks(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[AnthropicContentBlockParam]:
        """Convert blocks to Anthropic-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        document_with_merged_inline_variables = reduce_inline_variable_blocks(
            Provider.ANTHROPIC, blocks, document, MessageRole.ASSISTANT
        )
        return reduce_document_blocks(
            Provider.ANTHROPIC,
            MessageRole.ASSISTANT,
            document_with_merged_inline_variables,
        )

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[AnthropicMessageParam]:
        """Convert blocks to Anthropic-specific message parameter."""
        return [
            AnthropicMessageParam(
                content=cls.to_provider_content_blocks(blocks, context),
                role=MessageRole.ASSISTANT.value,
            )
        ]


class AdapterAnthropicToolCall(
    ProviderAdapter[ToolCall, AnthropicToolUseBlockParam, AnthropicMessageParam]
):
    """Adapter for Anthropic API."""

    PROVIDER = Provider.ANTHROPIC

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ToolCall]],
        context: MessageContext,
    ) -> Sequence[Sequence[AnthropicToolUseBlockParam]]:
        """Convert blocks to Anthropic-specific content document."""
        document = [
            [
                block.to_provider_content_block(Provider.ANTHROPIC, context)
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
    ) -> Sequence[AnthropicToolUseBlockParam]:
        """Convert blocks to Anthropic-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        return list(chain.from_iterable(document))

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ToolCall]],
        context: MessageContext,
    ) -> Sequence[AnthropicMessageParam]:
        """Convert blocks to Anthropic-specific message parameter."""
        return [
            AnthropicMessageParam(
                content=cls.to_provider_content_blocks(blocks, context),
                role=MessageRole.ASSISTANT.value,
            )
        ]


class AdapterAnthropicToolResult(
    ProviderAdapter[ToolResult, AnthropicToolResultBlockParam, AnthropicMessageParam]
):
    """Adapter for Anthropic API."""

    PROVIDER = Provider.ANTHROPIC

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ToolResult]],
        context: MessageContext,
    ) -> Sequence[Sequence[AnthropicToolResultBlockParam]]:
        """Convert blocks to Anthropic-specific content document."""
        document = [
            [
                block.to_provider_content_block(Provider.ANTHROPIC, context)
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
    ) -> Sequence[AnthropicToolResultBlockParam]:
        """Convert blocks to Anthropic-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        return list(chain.from_iterable(document))

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ToolResult]],
        context: MessageContext,
    ) -> Sequence[AnthropicMessageParam]:
        """Convert blocks to Anthropic-specific message parameter."""
        return [
            AnthropicMessageParam(
                content=cls.to_provider_content_blocks(blocks, context),
                role=MessageRole.USER.value,
            )
        ]
