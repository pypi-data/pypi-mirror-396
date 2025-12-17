"""OpenAI provider adapter implementation."""

from itertools import chain
from typing import Sequence, cast

from moxn.base_models.blocks.context import MessageContext
from moxn.base_models.blocks.tool import ToolCall, ToolResult
from moxn.base_models.content_block import ContentBlock
from moxn.base_models.providers.base import ProviderAdapter
from moxn.base_models.reducers.reducer_document import reduce_document_blocks
from moxn.base_models.reducers.reducer_inline_variable import (
    reduce_inline_variable_blocks,
)
from moxn.types.content import MessageRole, Provider
from moxn.types.type_aliases.openai_chat import (
    OpenAIChatAssistantMessageParam,
    OpenAIChatContentBlock,
    OpenAIChatDeveloperMessageParam,
    OpenAIChatSystemMessageParam,
    OpenAIChatToolResponseParam,
    OpenAIChatToolUseBlockParam,
    OpenAIChatUserMessageParam,
)


class AdapterOpenAIChatSystem(
    ProviderAdapter[
        ContentBlock,
        OpenAIChatContentBlock,
        OpenAIChatSystemMessageParam,
    ]
):
    """Adapter for OpenAI System messages."""

    PROVIDER = Provider.OPENAI_CHAT

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[Sequence[OpenAIChatContentBlock]]:
        """Convert blocks to OpenAI-specific content document."""
        document = [
            [
                block.to_provider_content_block(Provider.OPENAI_CHAT, context)
                for block in block_group
            ]
            for block_group in blocks
        ]
        return document

    @classmethod
    def to_provider_content_blocks(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[OpenAIChatContentBlock]:
        """Convert blocks to OpenAI-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        document_with_merged_inline_variables = reduce_inline_variable_blocks(
            Provider.OPENAI_CHAT, blocks, document, MessageRole.SYSTEM
        )
        return reduce_document_blocks(
            Provider.OPENAI_CHAT,
            MessageRole.SYSTEM,
            document_with_merged_inline_variables,
        )

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[OpenAIChatSystemMessageParam]:
        """Convert blocks to OpenAI-specific message parameter."""
        content_blocks = cls.to_provider_content_blocks(blocks, context)
        return [
            OpenAIChatSystemMessageParam(
                role=MessageRole.SYSTEM.value,
                content=cast(str | list, content_blocks),
            )
        ]


class AdapterOpenAIChatUser(
    ProviderAdapter[
        ContentBlock,
        OpenAIChatContentBlock,
        OpenAIChatUserMessageParam,
    ]
):
    """Adapter for OpenAI User messages."""

    PROVIDER = Provider.OPENAI_CHAT

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[Sequence[OpenAIChatContentBlock]]:
        """Convert blocks to OpenAI-specific content document."""
        document = [
            [
                block.to_provider_content_block(Provider.OPENAI_CHAT, context)
                for block in block_group
            ]
            for block_group in blocks
        ]
        return document

    @classmethod
    def to_provider_content_blocks(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[OpenAIChatContentBlock]:
        """Convert blocks to OpenAI-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        document_with_merged_inline_variables = reduce_inline_variable_blocks(
            Provider.OPENAI_CHAT, blocks, document, MessageRole.USER
        )
        return reduce_document_blocks(
            Provider.OPENAI_CHAT,
            MessageRole.USER,
            document_with_merged_inline_variables,
        )

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[OpenAIChatUserMessageParam]:
        """Convert blocks to OpenAI-specific message parameter."""
        content_blocks = cls.to_provider_content_blocks(blocks, context)
        return [
            OpenAIChatUserMessageParam(
                role=MessageRole.USER.value,
                content=cast(str | list, content_blocks),
            )
        ]


class AdapterOpenAIChatAssistant(
    ProviderAdapter[
        ContentBlock,
        OpenAIChatContentBlock,
        OpenAIChatAssistantMessageParam,
    ]
):
    """Adapter for OpenAI Assistant messages."""

    PROVIDER = Provider.OPENAI_CHAT

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[Sequence[OpenAIChatContentBlock]]:
        """Convert blocks to OpenAI-specific content document."""
        document = [
            [
                block.to_provider_content_block(Provider.OPENAI_CHAT, context)
                for block in block_group
            ]
            for block_group in blocks
        ]
        return document

    @classmethod
    def to_provider_content_blocks(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[OpenAIChatContentBlock]:
        """Convert blocks to OpenAI-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        document_with_merged_inline_variables = reduce_inline_variable_blocks(
            Provider.OPENAI_CHAT, blocks, document, MessageRole.ASSISTANT
        )
        return reduce_document_blocks(
            Provider.OPENAI_CHAT,
            MessageRole.ASSISTANT,
            document_with_merged_inline_variables,
        )

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[OpenAIChatAssistantMessageParam]:
        """Convert blocks to OpenAI-specific message parameter."""
        content_blocks = cls.to_provider_content_blocks(blocks, context)
        return [
            OpenAIChatAssistantMessageParam(
                role=MessageRole.ASSISTANT.value,
                content=cast(str | list, content_blocks),
            )
        ]


class AdapterOpenAIChatDeveloper(
    ProviderAdapter[
        ContentBlock,
        OpenAIChatContentBlock,
        OpenAIChatDeveloperMessageParam,
    ]
):
    """Adapter for OpenAI Developer messages."""

    PROVIDER = Provider.OPENAI_CHAT

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[Sequence[OpenAIChatContentBlock]]:
        """Convert blocks to OpenAI-specific content document."""
        document = [
            [
                block.to_provider_content_block(Provider.OPENAI_CHAT, context)
                for block in block_group
            ]
            for block_group in blocks
        ]
        return document

    @classmethod
    def to_provider_content_blocks(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[OpenAIChatContentBlock]:
        """Convert blocks to OpenAI-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        document_with_merged_inline_variables = reduce_inline_variable_blocks(
            Provider.OPENAI_CHAT, blocks, document, MessageRole.DEVELOPER
        )
        return reduce_document_blocks(
            Provider.OPENAI_CHAT,
            MessageRole.DEVELOPER,
            document_with_merged_inline_variables,
        )

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[OpenAIChatDeveloperMessageParam]:
        """Convert blocks to OpenAI-specific message parameter."""
        content_blocks = cls.to_provider_content_blocks(blocks, context)
        return [
            OpenAIChatDeveloperMessageParam(
                role=MessageRole.DEVELOPER.value,
                content=cast(str | list, content_blocks),
            )
        ]


class AdapterOpenAIChatToolCall(
    ProviderAdapter[
        ToolCall,
        OpenAIChatToolUseBlockParam,
        OpenAIChatAssistantMessageParam,
    ]
):
    """Adapter for OpenAI Tool Call messages."""

    PROVIDER = Provider.OPENAI_CHAT

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ToolCall]],
        context: MessageContext,
    ) -> Sequence[Sequence[OpenAIChatToolUseBlockParam]]:
        """Convert blocks to OpenAI-specific content document."""
        document = [
            [
                block.to_provider_content_block(Provider.OPENAI_CHAT, context)
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
    ) -> Sequence[OpenAIChatToolUseBlockParam]:
        """Convert blocks to OpenAI-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        return list(chain.from_iterable(document))

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ToolCall]],
        context: MessageContext,
    ) -> Sequence[OpenAIChatAssistantMessageParam]:
        """Convert blocks to OpenAI-specific message parameter."""
        content_blocks = cls.to_provider_content_blocks(blocks, context)
        return [
            OpenAIChatAssistantMessageParam(
                role="assistant",
                tool_calls=content_blocks,
            )
        ]


class AdapterOpenAIChatToolResult(
    ProviderAdapter[
        ToolResult, OpenAIChatToolResponseParam, OpenAIChatToolResponseParam
    ]
):
    """Adapter for OpenAI Tool Result messages."""

    PROVIDER = Provider.OPENAI_CHAT

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ToolResult]],
        context: MessageContext,
    ) -> Sequence[Sequence[OpenAIChatToolResponseParam]]:
        """Convert blocks to OpenAI-specific content document."""
        document = [
            [
                block.to_provider_content_block(Provider.OPENAI_CHAT, context)
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
    ) -> Sequence[OpenAIChatToolResponseParam]:
        """Convert blocks to OpenAI-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        return list(chain.from_iterable(document))

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ToolResult]],
        context: MessageContext,
    ) -> Sequence[OpenAIChatToolResponseParam]:
        """Convert blocks to OpenAI-specific message parameter."""
        # For tool results in OpenAI, we convert them to a tool message
        tool_result_blocks = cls.to_provider_content_blocks(blocks, context)
        return tool_result_blocks
