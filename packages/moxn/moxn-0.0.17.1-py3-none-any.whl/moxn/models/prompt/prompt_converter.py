"""Prompt-level conversion to provider-specific API payloads.

This module provides adapters that convert Moxn prompt sessions into
the exact TypedDict structures expected by provider SDKs.
"""

from abc import ABC, abstractmethod
from typing import Any, Literal, overload

from moxn.base_models.blocks.context import MessageContext
from moxn.models import message as msg
from moxn.types.content import MessageRole, Provider
from moxn.types.type_aliases.anthropic import AnthropicMessagesParam
from moxn.types.type_aliases.google import GoogleMessagesParam
from moxn.types.type_aliases.openai_chat import OpenAIChatMessagesParam
from moxn.types.type_aliases.openai_responses import OpenAIResponsesMessagesParam
from moxn.types.type_aliases.provider import ProviderPayload


class PromptAdapter(ABC):
    """Base adapter for converting prompt sessions to provider payloads."""

    @abstractmethod
    def convert(
        self,
        messages: list[msg.Message],
        context: MessageContext | None = None,
    ) -> ProviderPayload:
        """Convert messages to provider-specific API payload.

        Args:
            messages: List of Moxn messages to convert.
            context: Optional context for variable substitution.

        Returns:
            Provider-specific TypedDict that can be unpacked into SDK calls.
        """
        pass


class AnthropicPromptAdapter(PromptAdapter):
    """Converts prompt sessions to Anthropic API format."""

    def convert(
        self,
        messages: list[msg.Message],
        context: MessageContext | None = None,
    ) -> AnthropicMessagesParam:
        """Convert to Anthropic format with separate system field.

        Returns:
            AnthropicMessagesParam with:
            - system: System prompt (string or list of blocks)
            - messages: List of user/assistant messages
        """
        system_content: list[Any] = []
        conversation_messages: list[Any] = []

        # Process each message based on its role
        for message in messages:
            if message.role == MessageRole.SYSTEM:
                # Convert system message to content blocks
                system_params = message.to_message_params(Provider.ANTHROPIC, context)
                system_content.extend(system_params)
            else:
                # Convert user/assistant messages
                msg_params = message.to_message_params(Provider.ANTHROPIC, context)
                conversation_messages.extend(msg_params)

        # Build AnthropicMessagesParam structure
        result: dict[str, Any] = {}

        if system_content:
            # Flatten system content appropriately
            if len(system_content) == 1 and isinstance(system_content[0], dict):
                # Single text block - check if we can extract as string
                if system_content[0].get("type") == "text":
                    result["system"] = system_content[0].get("text", "")
                else:
                    result["system"] = system_content
            else:
                # Multiple blocks - keep as list
                result["system"] = system_content

        if conversation_messages:
            result["messages"] = conversation_messages

        return result  # type: ignore


class OpenAIPromptAdapter(PromptAdapter):
    """Converts prompt sessions to OpenAI Chat API format."""

    def convert(
        self,
        messages: list[msg.Message],
        context: MessageContext | None = None,
    ) -> OpenAIChatMessagesParam:
        """Convert to OpenAI format with all messages in single array.

        Returns:
            OpenAIChatMessagesParam with:
            - messages: List of all messages including system role
        """
        all_messages: list[Any] = []

        # OpenAI includes all messages (including system) in messages array
        for message in messages:
            msg_params = message.to_message_params(Provider.OPENAI_CHAT, context)
            all_messages.extend(msg_params)

        return {"messages": all_messages}  # type: ignore


class OpenAIResponsesPromptAdapter(PromptAdapter):
    """Converts prompt sessions to OpenAI Responses API format."""

    def convert(
        self,
        messages: list[msg.Message],
        context: MessageContext | None = None,
    ) -> OpenAIResponsesMessagesParam:
        """Convert to OpenAI Responses format with instructions + input items.

        Extracts system messages to the 'instructions' field (like Anthropic/Google pattern).

        Returns:
            OpenAIResponsesMessagesParam with:
            - input: List of message/tool items
            - instructions: System/developer message text (if any)
        """
        system_texts: list[str] = []
        input_items: list[Any] = []

        # Process each message based on its role
        for message in messages:
            if message.role == MessageRole.SYSTEM:
                # Extract system messages to instructions field
                system_params = message.to_message_params(
                    Provider.OPENAI_RESPONSES, context
                )
                # Extract text from the message item content blocks
                for item in system_params:
                    if isinstance(item, dict) and item.get("type") == "message":
                        content = item.get("content", [])
                        if isinstance(content, list):
                            for content_block in content:
                                if (
                                    isinstance(content_block, dict)
                                    and content_block.get("type") == "input_text"
                                ):
                                    system_texts.append(content_block.get("text", ""))
            else:
                # Convert user/assistant/tool messages to items
                msg_items = message.to_message_params(
                    Provider.OPENAI_RESPONSES, context
                )
                input_items.extend(msg_items)

        # Build OpenAIResponsesMessagesParam structure
        result: dict[str, Any] = {"input": input_items}

        if system_texts:
            result["instructions"] = "\n\n".join(system_texts)

        return result  # type: ignore


class GooglePromptAdapter(PromptAdapter):
    """Converts prompt sessions to Google (Gemini/Vertex) API format."""

    def convert(
        self,
        messages: list[msg.Message],
        context: MessageContext | None = None,
    ) -> GoogleMessagesParam:
        """Convert to Google format with system_instruction and content.

        Handles:
        - ASSISTANT → MODEL role mapping
        - Separate system_instruction field
        - Content array structure

        Returns:
            GoogleMessagesParam with:
            - system_instruction: Optional system instruction string
            - content: List of content messages with user/model roles
        """
        system_instructions: list[str] = []
        content_messages: list[Any] = []

        for message in messages:
            if message.role == MessageRole.SYSTEM:
                # Extract system instruction
                system_params = message.to_message_params(
                    Provider.GOOGLE_GEMINI, context
                )
                # Google system messages come as {'system_instruction': 'text'}
                for param in system_params:
                    if isinstance(param, dict):
                        if "system_instruction" in param:
                            system_instructions.append(
                                str(param.get("system_instruction", ""))
                            )
                        elif param.get("type") == "text":
                            system_instructions.append(str(param.get("text", "")))
                    elif isinstance(param, str):
                        system_instructions.append(param)
            else:
                # Handle user and assistant messages
                # Note: The role mapping (ASSISTANT → MODEL) should happen
                # in the message adapter layer, not here
                msg_params = message.to_message_params(Provider.GOOGLE_GEMINI, context)
                # Extract content from each GoogleMessagesParam and flatten
                for param in msg_params:
                    if isinstance(param, dict) and "content" in param:
                        content_messages.extend(param["content"])

        # Build GoogleMessagesParam structure
        result: dict[str, Any] = {}

        if system_instructions:
            # Combine system instructions into single string
            result["system_instruction"] = "\n".join(system_instructions)

        if content_messages:
            result["content"] = content_messages

        return result  # type: ignore


class PromptConverter:
    """Facade for prompt-level conversion to provider payloads."""

    # Registry of provider-specific adapters
    ADAPTERS: dict[Provider, PromptAdapter] = {
        Provider.ANTHROPIC: AnthropicPromptAdapter(),
        Provider.OPENAI_CHAT: OpenAIPromptAdapter(),
        Provider.OPENAI_RESPONSES: OpenAIResponsesPromptAdapter(),
        Provider.GOOGLE_GEMINI: GooglePromptAdapter(),
        Provider.GOOGLE_VERTEX: GooglePromptAdapter(),  # Same as Gemini
    }

    @overload
    @classmethod
    def to_provider_payload(
        cls,
        messages: list[msg.Message],
        provider: Literal[Provider.ANTHROPIC],
        context: MessageContext | None = None,
    ) -> AnthropicMessagesParam: ...

    @overload
    @classmethod
    def to_provider_payload(
        cls,
        messages: list[msg.Message],
        provider: Literal[Provider.OPENAI_CHAT],
        context: MessageContext | None = None,
    ) -> OpenAIChatMessagesParam: ...

    @overload
    @classmethod
    def to_provider_payload(
        cls,
        messages: list[msg.Message],
        provider: Literal[Provider.OPENAI_RESPONSES],
        context: MessageContext | None = None,
    ) -> OpenAIResponsesMessagesParam: ...

    @overload
    @classmethod
    def to_provider_payload(
        cls,
        messages: list[msg.Message],
        provider: Literal[Provider.GOOGLE_GEMINI, Provider.GOOGLE_VERTEX],
        context: MessageContext | None = None,
    ) -> GoogleMessagesParam: ...

    @overload
    @classmethod
    def to_provider_payload(
        cls,
        messages: list[msg.Message],
        provider: Provider,
        context: MessageContext | None = None,
    ) -> ProviderPayload: ...

    @classmethod
    def to_provider_payload(
        cls,
        messages: list[msg.Message],
        provider: Provider,
        context: MessageContext | None = None,
    ) -> ProviderPayload:
        """Convert messages to provider-specific API payload.

        Args:
            messages: List of Moxn messages to convert.
            provider: Target provider for conversion.
            context: Optional context for variable substitution.

        Returns:
            Provider-specific TypedDict ready for SDK usage.

        Raises:
            ValueError: If no adapter exists for the provider.
        """
        adapter = cls.ADAPTERS.get(provider)
        if not adapter:
            raise ValueError(f"No prompt adapter available for provider: {provider}")

        return adapter.convert(messages, context)

    @classmethod
    def register_adapter(cls, provider: Provider, adapter: PromptAdapter) -> None:
        """Register a custom adapter for a provider.

        Args:
            provider: Provider to register adapter for.
            adapter: Adapter instance to use for conversion.
        """
        cls.ADAPTERS[provider] = adapter
