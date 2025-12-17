from typing import Literal, overload

from moxn.models.response import ParsedResponse, ResponseParser
from moxn.types.content import Provider
from moxn.types.type_aliases.anthropic import AnthropicMessage
from moxn.types.type_aliases.google import GoogleGenerateContentResponse
from moxn.types.type_aliases.openai_chat import OpenAIChatCompletion
from moxn.types.type_aliases.openai_responses import OpenAIResponse
from moxn.types.type_aliases.provider import ProviderResponse


class ResponseHandler:
    """Handles parsing and processing of provider responses."""

    @overload
    @staticmethod
    def parse_provider_response(
        response: AnthropicMessage,
        provider: Literal[Provider.ANTHROPIC],
    ) -> ParsedResponse: ...

    @overload
    @staticmethod
    def parse_provider_response(
        response: OpenAIChatCompletion,
        provider: Literal[Provider.OPENAI_CHAT],
    ) -> ParsedResponse: ...

    @overload
    @staticmethod
    def parse_provider_response(
        response: OpenAIResponse,
        provider: Literal[Provider.OPENAI_RESPONSES],
    ) -> ParsedResponse: ...

    @overload
    @staticmethod
    def parse_provider_response(
        response: GoogleGenerateContentResponse,
        provider: Literal[Provider.GOOGLE_GEMINI, Provider.GOOGLE_VERTEX],
    ) -> ParsedResponse: ...

    @overload
    @staticmethod
    def parse_provider_response(
        response: ProviderResponse,
        provider: Provider,
    ) -> ParsedResponse: ...

    @staticmethod
    def parse_provider_response(
        response: ProviderResponse,
        provider: Provider,
    ) -> ParsedResponse:
        """Parse a provider response into a normalized format."""
        if provider == Provider.ANTHROPIC:
            if not isinstance(response, AnthropicMessage):
                raise TypeError(
                    f"Expected AnthropicMessage for Anthropic provider, got {type(response)}"
                )
            return ResponseParser.parse(response, provider)
        elif provider == Provider.OPENAI_CHAT:
            if not isinstance(response, OpenAIChatCompletion):
                raise TypeError(
                    f"Expected OpenAIChatCompletion for OpenAI provider, got {type(response)}"
                )
            return ResponseParser.parse(response, provider)
        elif provider == Provider.OPENAI_RESPONSES:
            if not isinstance(response, OpenAIResponse):
                raise TypeError(
                    f"Expected OpenAIResponse for OpenAI Responses provider, got {type(response)}"
                )
            return ResponseParser.parse(response, provider)
        elif provider == Provider.GOOGLE_GEMINI or provider == Provider.GOOGLE_VERTEX:
            if not isinstance(response, GoogleGenerateContentResponse):
                raise TypeError(
                    f"Expected GoogleGenerateContentResponse for Google provider, got {type(response)}"
                )
            return ResponseParser.parse(response, provider)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
