"""OpenAI Responses API provider adapter implementation."""

from itertools import chain
from typing import Sequence

from moxn.base_models.blocks.context import MessageContext
from moxn.base_models.blocks.tool import ToolCall, ToolResult
from moxn.base_models.content_block import ContentBlock
from moxn.base_models.providers.base import ProviderAdapter
from moxn.base_models.reducers.reducer_document import reduce_document_blocks
from moxn.base_models.reducers.reducer_inline_variable import (
    reduce_inline_variable_blocks,
)
from moxn.types.content import MessageRole, Provider
from moxn.types.type_aliases.openai_responses import (
    OpenAIResponsesContentBlock,
    OpenAIResponsesFunctionCallOutput,
    OpenAIResponsesFunctionToolCallParam,
)


class AdapterOpenAIResponsesMessage(
    ProviderAdapter[
        ContentBlock,
        OpenAIResponsesContentBlock,
        dict,  # Returns Message item as dict
    ]
):
    """Adapter for OpenAI Responses API Message items (user/system/developer roles)."""

    PROVIDER = Provider.OPENAI_RESPONSES

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[Sequence[OpenAIResponsesContentBlock]]:
        """Convert blocks to OpenAI Responses-specific content document."""
        document = [
            [
                block.to_provider_content_block(Provider.OPENAI_RESPONSES, context)
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
    ) -> Sequence[OpenAIResponsesContentBlock]:
        """Convert blocks to OpenAI Responses-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        document_with_merged_inline_variables = reduce_inline_variable_blocks(
            Provider.OPENAI_RESPONSES,
            blocks,
            document,
            MessageRole.USER,  # Message items use user/system/developer roles
        )
        return reduce_document_blocks(
            Provider.OPENAI_RESPONSES,
            MessageRole.USER,
            document_with_merged_inline_variables,
        )

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[dict]:
        """Convert blocks to OpenAI Responses Message item.

        Returns a list containing a single Message item dict with:
        - type: "message"
        - role: "user", "system", or "developer"
        - content: list of content blocks
        """
        content_blocks = cls.to_provider_content_blocks(blocks, context)

        # Message adapter is generic - role is determined by which adapter is used
        # For this base adapter, we default to "user" role
        # System/Developer adapters are aliased to this same class
        return [
            {
                "type": "message",
                "role": "user",  # Default role for generic message adapter
                "content": list(content_blocks),
            }
        ]


class AdapterOpenAIResponsesSystem(AdapterOpenAIResponsesMessage):
    """Adapter for system role messages."""

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[dict]:
        """Convert blocks to system Message item."""
        content_blocks = cls.to_provider_content_blocks(blocks, context)
        return [
            {
                "type": "message",
                "role": "system",
                "content": list(content_blocks),
            }
        ]


class AdapterOpenAIResponsesUser(AdapterOpenAIResponsesMessage):
    """Adapter for user role messages."""

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[dict]:
        """Convert blocks to user Message item."""
        content_blocks = cls.to_provider_content_blocks(blocks, context)
        return [
            {
                "type": "message",
                "role": "user",
                "content": list(content_blocks),
            }
        ]


class AdapterOpenAIResponsesDeveloper(AdapterOpenAIResponsesMessage):
    """Adapter for developer role messages."""

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[dict]:
        """Convert blocks to developer Message item."""
        content_blocks = cls.to_provider_content_blocks(blocks, context)
        return [
            {
                "type": "message",
                "role": "developer",
                "content": list(content_blocks),
            }
        ]


class AdapterOpenAIResponsesAssistant(
    ProviderAdapter[
        ContentBlock,
        OpenAIResponsesContentBlock,
        dict,
    ]
):
    """Adapter for OpenAI Responses API assistant messages.

    Note: In Responses API, assistant messages come from the output,
    not the input. This adapter handles cases where we're appending
    previous assistant responses to the conversation.
    """

    PROVIDER = Provider.OPENAI_RESPONSES

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[Sequence[OpenAIResponsesContentBlock]]:
        """Convert blocks to OpenAI Responses-specific content document."""
        document = [
            [
                block.to_provider_content_block(Provider.OPENAI_RESPONSES, context)  # type: ignore
                for block in block_group
            ]
            for block_group in blocks
        ]
        return document  # type: ignore

    @classmethod
    def to_provider_content_blocks(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[OpenAIResponsesContentBlock]:
        """Convert blocks to OpenAI Responses-specific content blocks."""
        document = cls.to_provider_content_document(blocks, context)
        document_with_merged_inline_variables = reduce_inline_variable_blocks(
            Provider.OPENAI_RESPONSES, blocks, document, MessageRole.USER
        )
        return reduce_document_blocks(
            Provider.OPENAI_RESPONSES,
            MessageRole.USER,
            document_with_merged_inline_variables,
        )

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ContentBlock]],
        context: MessageContext,
    ) -> Sequence[dict]:
        """Convert blocks to ResponseOutputMessage item (from previous responses)."""
        content_blocks = cls.to_provider_content_blocks(blocks, context)

        return [
            {
                "type": "message",
                "role": "assistant",
                "content": list(content_blocks),
            }
        ]


class AdapterOpenAIResponsesToolCall(
    ProviderAdapter[
        ToolCall,
        OpenAIResponsesFunctionToolCallParam,
        dict,
    ]
):
    """Adapter for OpenAI Responses API function tool calls."""

    PROVIDER = Provider.OPENAI_RESPONSES

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ToolCall]],
        context: MessageContext,
    ) -> Sequence[Sequence[OpenAIResponsesFunctionToolCallParam]]:
        """Convert tool call blocks to OpenAI Responses format."""
        document = [
            [
                block.to_provider_content_block(Provider.OPENAI_RESPONSES, context)  # type: ignore
                for block in block_group
            ]
            for block_group in blocks
        ]
        return document  # type: ignore

    @classmethod
    def to_provider_content_blocks(
        cls,
        blocks: Sequence[Sequence[ToolCall]],
        context: MessageContext,
    ) -> Sequence[OpenAIResponsesFunctionToolCallParam]:
        """Convert tool call blocks to flat sequence."""
        document = cls.to_provider_content_document(blocks, context)
        return list(chain.from_iterable(document))

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ToolCall]],
        context: MessageContext,
    ) -> Sequence[dict]:
        """Convert tool calls to function_call items.

        In Responses API, tool calls are separate items, not embedded in messages.
        Each tool call becomes its own item in the input array.
        """
        tool_call_blocks = cls.to_provider_content_blocks(blocks, context)

        # Each tool call is already a complete item (has type="function_call")
        # Return as list of dicts
        return list(tool_call_blocks)  # type: ignore


class AdapterOpenAIResponsesToolResult(
    ProviderAdapter[
        ToolResult,
        OpenAIResponsesFunctionCallOutput,
        dict,
    ]
):
    """Adapter for OpenAI Responses API function call outputs."""

    PROVIDER = Provider.OPENAI_RESPONSES

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[ToolResult]],
        context: MessageContext,
    ) -> Sequence[Sequence[OpenAIResponsesFunctionCallOutput]]:
        """Convert tool result blocks to OpenAI Responses format."""
        document = [
            [
                block.to_provider_content_block(Provider.OPENAI_RESPONSES, context)  # type: ignore
                for block in block_group
            ]
            for block_group in blocks
        ]
        return document  # type: ignore

    @classmethod
    def to_provider_content_blocks(
        cls,
        blocks: Sequence[Sequence[ToolResult]],
        context: MessageContext,
    ) -> Sequence[OpenAIResponsesFunctionCallOutput]:
        """Convert tool result blocks to flat sequence."""
        document = cls.to_provider_content_document(blocks, context)
        return list(chain.from_iterable(document))

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[ToolResult]],
        context: MessageContext,
    ) -> Sequence[dict]:
        """Convert tool results to function_call_output items.

        In Responses API, tool results are separate items, not embedded in messages.
        Each result becomes its own item in the input array.
        """
        tool_result_blocks = cls.to_provider_content_blocks(blocks, context)

        # Each tool result is already a complete item (has type="function_call_output")
        return list(tool_result_blocks)  # type: ignore
