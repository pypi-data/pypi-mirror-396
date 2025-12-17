from typing import Any, Literal, overload

from moxn.base_models.blocks.base import ToProviderContentBlockMixin
from moxn.base_models.blocks.context import MessageContext
from moxn.types.blocks.text import (
    ReasoningContentModel,
    TextContentModel,
    ThinkingContentModel,
)
from moxn.types.content import Provider
from moxn.types.type_aliases.anthropic import AnthropicTextBlockParam
from moxn.types.type_aliases.google import GooglePart
from moxn.types.type_aliases.openai_chat import (
    OpenAIChatCompletionContentPartTextParam,
)
from moxn.types.type_aliases.openai_responses import (
    OpenAIResponsesInputTextParam,
)


class ToProviderContentBlockMixinTextOnly(
    ToProviderContentBlockMixin
):  # Override the to_provider_content_block method with more specific types
    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.ANTHROPIC], context: MessageContext
    ) -> AnthropicTextBlockParam: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.OPENAI_CHAT], context: MessageContext
    ) -> OpenAIChatCompletionContentPartTextParam: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.OPENAI_RESPONSES], context: MessageContext
    ) -> OpenAIResponsesInputTextParam: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.GOOGLE_GEMINI], context: MessageContext
    ) -> GooglePart: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.GOOGLE_VERTEX], context: MessageContext
    ) -> GooglePart: ...

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
    ) -> AnthropicTextBlockParam:
        raise NotImplementedError

    def _to_openai_chat_content_block(
        self, context: MessageContext
    ) -> OpenAIChatCompletionContentPartTextParam:
        raise NotImplementedError

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputTextParam:
        raise NotImplementedError

    def _to_google_gemini_content_block(self, context: MessageContext) -> GooglePart:
        raise NotImplementedError

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        raise NotImplementedError


class TextContent(TextContentModel, ToProviderContentBlockMixinTextOnly):
    """Text content block."""

    text: str

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicTextBlockParam:
        return AnthropicTextBlockParam(type="text", text=self.text)

    def _to_openai_chat_content_block(
        self, context: MessageContext
    ) -> OpenAIChatCompletionContentPartTextParam:
        return OpenAIChatCompletionContentPartTextParam(type="text", text=self.text)

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputTextParam:
        return OpenAIResponsesInputTextParam(type="input_text", text=self.text)

    def _to_google_gemini_content_block(self, context: MessageContext) -> GooglePart:
        return GooglePart.from_text(text=self.text)

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        return GooglePart.from_text(text=self.text)


class ThinkingContent(ThinkingContentModel, ToProviderContentBlockMixinTextOnly):
    """Thinking content block with bidirectional provider support.

    Used for Claude's extended thinking and Gemini's thinking parts.
    When round-tripping to providers that don't support thinking blocks,
    the content is converted to a text block with a [Thinking] prefix.
    """

    thinking: str

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> dict[str, Any]:
        # Anthropic supports thinking blocks natively
        return {"type": "thinking", "thinking": self.thinking}

    def _to_openai_chat_content_block(
        self, context: MessageContext
    ) -> OpenAIChatCompletionContentPartTextParam:
        # OpenAI doesn't support thinking in requests - convert to text
        return OpenAIChatCompletionContentPartTextParam(
            type="text", text=f"[Thinking]\n{self.thinking}"
        )

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputTextParam:
        # OpenAI Responses doesn't support thinking in requests - convert to text
        return OpenAIResponsesInputTextParam(
            type="input_text", text=f"[Thinking]\n{self.thinking}"
        )

    def _to_google_gemini_content_block(self, context: MessageContext) -> GooglePart:
        # Google may support thinking parts - convert to text for now
        return GooglePart.from_text(text=f"[Thinking]\n{self.thinking}")

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        return GooglePart.from_text(text=f"[Thinking]\n{self.thinking}")


class ReasoningContent(ReasoningContentModel, ToProviderContentBlockMixinTextOnly):
    """Reasoning content block for OpenAI o1/o3 model reasoning summaries.

    When round-tripping to providers, the reasoning summary is converted
    to a text block with a [Reasoning] prefix.
    """

    summary: str

    def _to_anthropic_content_block(
        self, context: MessageContext
    ) -> AnthropicTextBlockParam:
        # Anthropic doesn't have reasoning - convert to text
        return AnthropicTextBlockParam(
            type="text", text=f"[Reasoning]\n{self.summary}"
        )

    def _to_openai_chat_content_block(
        self, context: MessageContext
    ) -> OpenAIChatCompletionContentPartTextParam:
        # Reasoning is output-only in o1/o3 - convert to text for round-trip
        return OpenAIChatCompletionContentPartTextParam(
            type="text", text=f"[Reasoning]\n{self.summary}"
        )

    def _to_openai_responses_content_block(
        self, context: MessageContext
    ) -> OpenAIResponsesInputTextParam:
        return OpenAIResponsesInputTextParam(
            type="input_text", text=f"[Reasoning]\n{self.summary}"
        )

    def _to_google_gemini_content_block(self, context: MessageContext) -> GooglePart:
        return GooglePart.from_text(text=f"[Reasoning]\n{self.summary}")

    def _to_google_vertex_content_block(self, context: MessageContext) -> GooglePart:
        return GooglePart.from_text(text=f"[Reasoning]\n{self.summary}")
