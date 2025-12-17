from __future__ import annotations

from typing import Any, Literal, overload

from moxn.base_models.blocks.context import MessageContext
from moxn.types.blocks.base import BaseContent as BaseContentModel
from moxn.types.content import Provider

# Provider types are imported conditionally to avoid forcing dependencies
from moxn.types.type_aliases.anthropic import (
    AnthropicContentBlockParam,
)
from moxn.types.type_aliases.google import (
    GoogleContentBlock,
)
from moxn.types.type_aliases.openai_chat import (
    OpenAIChatContentBlock,
)
from moxn.types.type_aliases.openai_responses import (
    OpenAIResponsesContentBlock,
)


class ToProviderContentBlockMixin(BaseContentModel):
    options: dict[str, Any] = {}

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.ANTHROPIC], context: MessageContext
    ) -> AnthropicContentBlockParam: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.OPENAI_CHAT], context: MessageContext
    ) -> OpenAIChatContentBlock: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.OPENAI_RESPONSES], context: MessageContext
    ) -> OpenAIResponsesContentBlock: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.GOOGLE_GEMINI], context: MessageContext
    ) -> GoogleContentBlock: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.GOOGLE_VERTEX], context: MessageContext
    ) -> GoogleContentBlock: ...

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
        self,
        context: MessageContext,
    ) -> AnthropicContentBlockParam:
        raise NotImplementedError

    def _to_openai_chat_content_block(
        self,
        context: MessageContext,
    ) -> OpenAIChatContentBlock:
        raise NotImplementedError

    def _to_openai_responses_content_block(
        self,
        context: MessageContext,
    ) -> OpenAIResponsesContentBlock:
        raise NotImplementedError

    def _to_google_gemini_content_block(
        self,
        context: MessageContext,
    ) -> GoogleContentBlock:
        raise NotImplementedError

    def _to_google_vertex_content_block(
        self,
        context: MessageContext,
    ) -> GoogleContentBlock:
        raise NotImplementedError
