import json
from typing import Any, Iterable, Literal, cast, overload

from moxn.base_models.blocks.base import ToProviderContentBlockMixin
from moxn.base_models.blocks.context import MessageContext
from moxn.base_models.blocks.image import ImageContentFromSource
from moxn.base_models.blocks.text import TextContent
from moxn.types.blocks.tool import ToolCallModel, ToolResultBase
from moxn.types.content import Provider
from moxn.types.type_aliases.anthropic import (
    AnthropicCacheControlEphemeralParam,
    AnthropicContent,
    AnthropicToolResultBlockParam,
    AnthropicToolUseBlockParam,
)
from moxn.types.type_aliases.google import (
    GoogleFunctionCall,
    GoogleFunctionResponse,
)
from moxn.types.type_aliases.openai_chat import (
    OpenAIChatFunction,
    OpenAIChatToolResponseParam,
    OpenAIChatToolUseBlockParam,
)
from moxn.types.type_aliases.openai_responses import (
    OpenAIResponsesFunctionCallOutput,
    OpenAIResponsesFunctionToolCallParam,
)


def coerce_args_to_str(args: str | dict[str, Any]) -> str:
    if isinstance(args, str):
        return args
    elif isinstance(args, dict):
        return json.dumps(args)
    else:
        raise ValueError("Arguments must be a string or a dictionary")


def coerce_args_to_dict(args: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(args, str):
        return json.loads(args)
    elif isinstance(args, dict):
        return args
    else:
        raise ValueError("Arguments must be a string or a dictionary")


class ToolCall(ToolCallModel, ToProviderContentBlockMixin):
    id: str
    arguments: str | dict[str, Any] | None
    name: str

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.ANTHROPIC], context: MessageContext
    ) -> AnthropicToolUseBlockParam: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.OPENAI_CHAT], context: MessageContext
    ) -> OpenAIChatToolUseBlockParam: ...

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.OPENAI_RESPONSES], context: MessageContext
    ) -> OpenAIResponsesFunctionToolCallParam: ...

    @overload
    def to_provider_content_block(
        self,
        provider: Literal[Provider.GOOGLE_GEMINI],
        context: MessageContext,
    ) -> GoogleFunctionCall: ...

    @overload
    def to_provider_content_block(
        self,
        provider: Literal[Provider.GOOGLE_VERTEX],
        context: MessageContext,
    ) -> GoogleFunctionCall: ...

    def to_provider_content_block(
        self, provider: Provider, context: MessageContext
    ) -> (
        AnthropicToolUseBlockParam
        | OpenAIChatToolUseBlockParam
        | OpenAIResponsesFunctionToolCallParam
        | GoogleFunctionCall
    ):
        if provider == Provider.ANTHROPIC:
            if self.arguments is None:
                raise ValueError("Arguments must be provided for Anthropic")
            else:
                args = coerce_args_to_dict(self.arguments)
            cache_control = cast(
                AnthropicCacheControlEphemeralParam | None,
                (
                    context.provider_settings.get(provider, {}).get(
                        "cache_control", None
                    )
                ),
            )

            if cache_control is not None:
                return AnthropicToolUseBlockParam(
                    id=self.id,
                    input=args,
                    name=self.name,
                    type="tool_use",
                    cache_control=cache_control,
                )
            else:
                return AnthropicToolUseBlockParam(
                    id=self.id,
                    input=args,
                    name=self.name,
                    type="tool_use",
                )
        elif provider == Provider.OPENAI_CHAT:
            if self.arguments is None:
                raise ValueError("Arguments must be provided for OpenAI")
            else:
                _args = coerce_args_to_str(self.arguments)

            return OpenAIChatToolUseBlockParam(
                id=self.id,
                function=OpenAIChatFunction(
                    name=self.name,
                    arguments=_args,
                ),
                type="function",
            )
        elif provider == Provider.OPENAI_RESPONSES:
            if self.arguments is None:
                raise ValueError("Arguments must be provided for OpenAI Responses")
            else:
                _args = coerce_args_to_str(self.arguments)

            return OpenAIResponsesFunctionToolCallParam(
                call_id=self.id,
                name=self.name,
                arguments=_args,
                type="function_call",
            )
        elif provider in (Provider.GOOGLE_GEMINI, Provider.GOOGLE_VERTEX):
            if self.arguments is None:
                args = None
            else:
                args = coerce_args_to_dict(self.arguments)
            return GoogleFunctionCall(
                name=self.name,
                args=args,
            )
        raise ValueError(f"Provider {provider} not supported")


class ToolResult(ToolResultBase[TextContent | ImageContentFromSource | None]):
    type: Literal["tool_use"]
    id: str
    name: str
    content: TextContent | ImageContentFromSource | None

    @overload
    def to_provider_content_block(
        self, provider: Literal[Provider.ANTHROPIC], context: MessageContext
    ) -> AnthropicToolResultBlockParam: ...

    @overload
    def to_provider_content_block(
        self,
        provider: Literal[Provider.OPENAI_CHAT],
        context: MessageContext,
    ) -> OpenAIChatToolResponseParam: ...

    @overload
    def to_provider_content_block(
        self,
        provider: Literal[Provider.OPENAI_RESPONSES],
        context: MessageContext,
    ) -> OpenAIResponsesFunctionCallOutput: ...

    @overload
    def to_provider_content_block(
        self,
        provider: Literal[Provider.GOOGLE_GEMINI, Provider.GOOGLE_VERTEX],
        context: MessageContext,
    ) -> GoogleFunctionResponse: ...

    def to_provider_content_block(
        self, provider: Provider, context: MessageContext
    ) -> (
        AnthropicToolResultBlockParam
        | OpenAIChatToolResponseParam
        | OpenAIResponsesFunctionCallOutput
        | GoogleFunctionResponse
    ):
        if provider == Provider.ANTHROPIC:
            if self.content is None:
                raise ValueError("Content must be provided for Anthropic")
            cache_control = cast(
                AnthropicCacheControlEphemeralParam | None,
                context.provider_settings.get(provider, {}).get("cache_control", None),
            )
            if cache_control is not None:
                return AnthropicToolResultBlockParam(
                    tool_use_id=self.id,
                    type="tool_result",
                    content=cast(
                        Iterable[AnthropicContent],
                        [
                            self.content.to_provider_content_block(
                                provider,
                                MessageContext(
                                    provider=provider,
                                    variables={},
                                    provider_settings={},
                                    metadata={},
                                ),
                            ),
                        ],
                    ),
                    cache_control=cache_control,
                )
            else:
                return AnthropicToolResultBlockParam(
                    tool_use_id=self.id,
                    type="tool_result",
                    content=cast(
                        Iterable[AnthropicContent],
                        [self.content.to_provider_content_block(provider, context)],
                    ),
                )
        elif provider == Provider.OPENAI_CHAT:
            if self.content is None or not isinstance(self.content, TextContent):
                raise ValueError("Content must be provided for OpenAI")
            return OpenAIChatToolResponseParam(
                tool_call_id=self.id,
                content=self.content.text,
                role="tool",
            )
        elif provider == Provider.OPENAI_RESPONSES:
            if self.content is None or not isinstance(self.content, TextContent):
                raise ValueError("Content must be text for OpenAI Responses")
            return OpenAIResponsesFunctionCallOutput(
                call_id=self.id,
                output=self.content.text,
                type="function_call_output",
            )
        elif provider in (Provider.GOOGLE_GEMINI, Provider.GOOGLE_VERTEX):
            if self.content is not None and isinstance(self.content, TextContent):
                try:
                    content = json.loads(self.content.text)
                except json.JSONDecodeError:
                    # If not valid JSON, wrap text as response
                    content = {"result": self.content.text} if self.content.text else None
            elif self.content is None:
                content = None
            else:
                raise ValueError("Content must be a string for Google Gemini or Vertex")
            return GoogleFunctionResponse(
                id=self.id,
                name=self.name,
                response=content,
            )

        else:
            raise ValueError(f"Provider {provider} not supported")
