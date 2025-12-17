from itertools import chain
from typing import Literal, Sequence, Union, overload

from moxn.base_models.blocks.context import MessageContext
from moxn.models import message as msg
from moxn.types.content import Provider
from moxn.types.type_aliases.anthropic import (
    AnthropicMessageParam,
    AnthropicTextBlockParam,
)
from moxn.types.type_aliases.google import GoogleContent
from moxn.types.type_aliases.openai_chat import (
    OpenAIChatSystemMessageParam,
    OpenAIChatUserMessageParam,
    OpenAIChatAssistantMessageParam,
)
from moxn.types.type_aliases.provider import ProviderMessageParam


class MessageConverter:
    """Handles conversion of messages to provider-specific message-level blocks.

    Note: This converter produces message-level content blocks, not complete
    API payloads. For prompt-level conversion that produces the complete
    TypedDicts expected by provider SDKs, use PromptConverter instead.
    """

    @overload
    @staticmethod
    def to_message_params(
        messages: list[msg.Message],
        provider: Literal[Provider.ANTHROPIC],
        context: MessageContext | dict | None = None,
    ) -> Sequence[Union[AnthropicTextBlockParam, AnthropicMessageParam]]: ...

    @overload
    @staticmethod
    def to_message_params(
        messages: list[msg.Message],
        provider: Literal[Provider.OPENAI_CHAT],
        context: MessageContext | dict | None = None,
    ) -> Sequence[
        Union[
            OpenAIChatSystemMessageParam,
            OpenAIChatUserMessageParam,
            OpenAIChatAssistantMessageParam,
        ]
    ]: ...

    @overload
    @staticmethod
    def to_message_params(
        messages: list[msg.Message],
        provider: Literal[Provider.GOOGLE_GEMINI, Provider.GOOGLE_VERTEX],
        context: MessageContext | dict | None = None,
    ) -> Sequence[GoogleContent]: ...

    @overload
    @staticmethod
    def to_message_params(
        messages: list[msg.Message],
        provider: Provider,
        context: MessageContext | dict | None = None,
    ) -> Sequence[ProviderMessageParam]: ...

    @staticmethod
    def to_message_params(
        messages: list[msg.Message],
        provider: Provider,
        context: MessageContext | dict | None = None,
    ) -> Sequence[ProviderMessageParam]:
        """Convert messages to provider-specific format."""
        if context is None:
            context = MessageContext.create_empty()
        elif isinstance(context, dict):
            context = MessageContext.from_variables(context)
        elif not isinstance(context, MessageContext):
            raise ValueError(f"Unsupported context type: {type(context)}")

        message_params = list(
            chain.from_iterable(
                msg.to_message_params(provider, context) for msg in messages
            )
        )
        return message_params  # type: ignore
