"""
Module for parsing and normalizing LLM responses across different providers.
"""

import json
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Type, cast, overload
from uuid import uuid4

from httpx._types import ResponseContent
from pydantic import ConfigDict, Field

from moxn.base_models.blocks.text import ReasoningContent, TextContent, ThinkingContent
from moxn.base_models.blocks.tool import ToolCall
from moxn.types.content import Provider
from moxn.types.request_config import RequestConfig
from moxn.types.response import (
    ParsedResponseCandidateModelBase,
    ParsedResponseModelBase,
    ResponseMetadata,
    ResponseParserProtocol,
    StopReason,
    TokenUsage,
)
from moxn.types.telemetry import LLMEventModelBase, ResponseType
from moxn.types.type_aliases.anthropic import (
    AnthropicContentBlock,
    AnthropicMessage,
    AnthropicToolUseBlock,
)
from moxn.types.type_aliases.google import (
    GoogleGenerateContentResponse,
    GoogleGenerateContentResponseCandidate,
)
from moxn.types.type_aliases.openai_chat import (
    OpenAIChatCompletion,
)
from moxn.types.type_aliases.openai_responses import OpenAIResponse

if TYPE_CHECKING:
    from moxn.models.message import Message
else:
    Message = Any


class ParsedResponseCandidate(
    ParsedResponseCandidateModelBase[TextContent, ToolCall, ThinkingContent, ReasoningContent]
):
    """Normalized response candidate with ordered content blocks.

    Content blocks preserve the order from the provider response, which is important
    for interleaved thinking/text/tool_call sequences in extended thinking models.
    """

    model_config = ConfigDict(populate_by_name=True)

    content_blocks: list[TextContent | ToolCall | ThinkingContent | ReasoningContent] = Field(
        alias="contentBlocks"
    )
    metadata: ResponseMetadata


class ParsedResponse(ParsedResponseModelBase[ParsedResponseCandidate]):
    """
    Normalized response content from any LLM provider.

    Contains parsed content blocks, metadata, and original response for reference.
    """

    candidates: list[ParsedResponseCandidate]

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ResponseParserAnthropic(ResponseParserProtocol[AnthropicMessage, ParsedResponse]):
    """Parser for Anthropic Claude responses."""

    @staticmethod
    def parse_candidate(
        response_content: list[AnthropicContentBlock | AnthropicToolUseBlock],
        stop_reason: StopReason,
        raw_stop_reason: str | None,
    ) -> ParsedResponseCandidate:
        """Parse a single Anthropic response candidate.

        Preserves the order of content blocks including thinking blocks for
        extended thinking models (Claude with thinking enabled).
        """
        content_blocks: list[TextContent | ToolCall | ThinkingContent | ReasoningContent] = []

        # Parse content blocks in order (preserving interleaved thinking/text/tool)
        if ResponseContent:
            for block in response_content:
                if block.type == "thinking":
                    # Handle thinking blocks (extended thinking models)
                    thinking_text = getattr(block, "thinking", "")
                    content_blocks.append(ThinkingContent(thinking=thinking_text))
                elif block.type == "redacted_thinking":
                    # Handle redacted thinking blocks - content is hidden
                    content_blocks.append(ThinkingContent(thinking="[REDACTED]"))
                elif block.type == "text" and block.text:
                    text_block = TextContent(text=block.text)
                    content_blocks.append(text_block)
                elif (
                    block.type == "tool_use"
                    and isinstance(block, AnthropicToolUseBlock)
                    and block.id
                    and block.name
                    and block.input
                ):
                    # Anthropic arguments are already a dict
                    tool_call = ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=cast(str | dict[str, Any] | None, block.input),
                    )
                    content_blocks.append(tool_call)

        return ParsedResponseCandidate(
            content_blocks=content_blocks,
            metadata=ResponseMetadata(
                normalized_finish_reason=stop_reason,
                raw_finish_reason=raw_stop_reason or "",
            ),
        )

    @classmethod
    def parse_response(
        cls, response: AnthropicMessage, provider: Provider = Provider.ANTHROPIC
    ) -> ParsedResponse:
        """Parse an Anthropic response into a normalized format."""
        stop_reason = StopReason.END_TURN
        raw_stop_reason = response.stop_reason

        # Anthropic stop reasons: ["end_turn", "max_tokens", "stop_sequence", "tool_use"]]
        if response.stop_reason == "end_turn":
            stop_reason = StopReason.END_TURN
        elif response.stop_reason == "tool_use":
            stop_reason = StopReason.TOOL_CALL
        elif response.stop_reason == "max_tokens":
            stop_reason = StopReason.MAX_TOKENS
        elif response.stop_reason == "stop_sequence":
            stop_reason = StopReason.END_TURN
        else:
            stop_reason = StopReason.OTHER

        # Parse candidate (Anthropic has only one candidate)
        candidates = [
            cls.parse_candidate(response.content, stop_reason, raw_stop_reason)
        ]

        # Extract token usage
        thinking_tokens = None
        if response.usage:
            # Check for thinking tokens in Anthropic's extended response
            # (future-proofing for when Anthropic adds thinking token tracking)
            if hasattr(response.usage, "cache_creation_input_tokens"):
                # Currently Anthropic doesn't have explicit thinking tokens in usage
                # but we prepare for future additions
                pass
        usage = TokenUsage(
            input_tokens=response.usage.input_tokens if response.usage else 0,
            completion_tokens=response.usage.output_tokens if response.usage else 0,
            thinking_tokens=thinking_tokens,
        )

        return ParsedResponse(
            provider=provider,
            candidates=candidates,
            stop_reason=stop_reason,
            usage=usage,
            model=response.model,
            raw_response=response.model_dump(by_alias=True, mode="json"),
        )

    @classmethod
    def extract_metadata(cls, response: AnthropicMessage) -> dict[str, Any]:
        """Extract additional metadata from Anthropic response."""
        metadata = {}

        # Add any Anthropic-specific metadata
        if hasattr(response, "id"):
            metadata["anthropic_message_id"] = response.id

        return metadata


class ResponseParserOpenAI(
    ResponseParserProtocol[OpenAIChatCompletion, ParsedResponse]
):
    """Parser for OpenAI responses."""

    @staticmethod
    def parse_candidate(message, finish_reason) -> ParsedResponseCandidate:
        """Parse a single OpenAI response candidate.

        For o1/o3 models, captures reasoning content as ReasoningContent blocks.
        Content blocks are ordered: reasoning (if present) -> text -> tool_calls.
        """
        content_blocks: list[TextContent | ToolCall | ThinkingContent | ReasoningContent] = []

        # Map OpenAI stop reasons to our normalized format
        if finish_reason == "stop":
            stop_reason = StopReason.END_TURN
        elif finish_reason == "length":
            stop_reason = StopReason.MAX_TOKENS
        elif finish_reason in ("tool_calls", "function_call"):
            stop_reason = StopReason.TOOL_CALL
        elif finish_reason == "content_filter":
            stop_reason = StopReason.CONTENT_FILTER
        else:
            stop_reason = StopReason.OTHER

        # Check for reasoning content (o1/o3 models)
        # reasoning_content appears before the main content in o-series responses
        reasoning_content = getattr(message, "reasoning_content", None)
        if reasoning_content:
            content_blocks.append(ReasoningContent(summary=reasoning_content))

        # Parse main content
        if message.content:
            content_blocks.append(TextContent(text=message.content))

        # Parse tool calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                # OpenAI tool calls have arguments as a string that needs to be parsed
                args = tool_call.function.arguments
                try:
                    # Convert string arguments to dict
                    args_dict = json.loads(args) if isinstance(args, str) else args
                except json.JSONDecodeError:
                    args_dict = {"raw_arguments": args}

                tool_call_obj = ToolCall(
                    id=tool_call.id, name=tool_call.function.name, arguments=args_dict
                )
                content_blocks.append(tool_call_obj)

        return ParsedResponseCandidate(
            content_blocks=content_blocks,
            metadata=ResponseMetadata(
                normalized_finish_reason=stop_reason, raw_finish_reason=finish_reason
            ),
        )

    @classmethod
    def parse_response(
        cls, response: OpenAIChatCompletion, provider: Provider = Provider.OPENAI_CHAT
    ) -> ParsedResponse:
        """Parse an OpenAI response into a normalized format."""
        candidates: list[ParsedResponseCandidate] = []

        # Get the choices from the response
        if not response.choices:
            return ParsedResponse(
                provider=provider,
                candidates=[],
                stop_reason=StopReason.ERROR,
                raw_response=response.model_dump(by_alias=True, mode="json"),
            )

        # Parse each choice as a candidate
        for choice in response.choices:
            candidates.append(cls.parse_candidate(choice.message, choice.finish_reason))

        # Extract token usage including reasoning tokens
        thinking_tokens = None
        if response.usage:
            # Check for reasoning_tokens in completion_tokens_details (o-series, GPT-5)
            completion_details = getattr(
                response.usage, "completion_tokens_details", None
            )
            if completion_details:
                thinking_tokens = getattr(completion_details, "reasoning_tokens", None)
        usage = TokenUsage(
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            thinking_tokens=thinking_tokens,
        )

        # Use the first candidate's stop reason for the overall response
        stop_reason = (
            candidates[0].metadata.normalized_finish_reason
            if candidates
            else StopReason.ERROR
        )

        return ParsedResponse(
            provider=provider,
            candidates=candidates,
            stop_reason=stop_reason,
            usage=usage,
            model=response.model,
            raw_response=response.model_dump(by_alias=True, mode="json"),
        )

    @classmethod
    def extract_metadata(cls, response: OpenAIChatCompletion) -> dict[str, Any]:
        """Extract additional metadata from OpenAI response."""
        metadata = {}

        # Add any OpenAI-specific metadata
        if response.id:
            metadata["openai_completion_id"] = response.id

        # Add system fingerprint if available
        if response.system_fingerprint:
            metadata["system_fingerprint"] = response.system_fingerprint

        return metadata


class ResponseParserGoogle(
    ResponseParserProtocol[GoogleGenerateContentResponse, ParsedResponse]
):
    """Parser for Google Gemini and Vertex responses."""

    @staticmethod
    def parse_candidate(
        candidate: GoogleGenerateContentResponseCandidate,
    ) -> ParsedResponseCandidate:
        """Parse a single Google response candidate.

        Preserves the order of parts including thinking parts for Gemini models
        with thinking enabled.
        """
        content_blocks: list[TextContent | ToolCall | ThinkingContent | ReasoningContent] = []
        finish_reason = (
            candidate.finish_reason.value.upper() if candidate.finish_reason else ""
        )
        if "STOP" in finish_reason:
            stop_reason = StopReason.END_TURN
        elif "MAX_TOKENS" in finish_reason:
            stop_reason = StopReason.MAX_TOKENS
        elif "SAFETY" in finish_reason or "BLOCK" in finish_reason:
            stop_reason = StopReason.CONTENT_FILTER
        elif "RECITATION" in finish_reason:
            stop_reason = StopReason.ERROR
        else:
            stop_reason = StopReason.OTHER

        # Parse content parts in order (preserving interleaved thinking/text/tool)
        content = candidate.content
        if content:
            if content.parts:
                for part in content.parts:
                    # Check for thinking/thought parts (Gemini 2.5+)
                    # thought is a boolean flag - if True, the text is thinking content
                    is_thought = getattr(part, "thought", None)
                    if is_thought is True and part.text:
                        content_blocks.append(ThinkingContent(thinking=part.text))
                    elif part.text:
                        text_content = TextContent(text=part.text)
                        content_blocks.append(text_content)
                    elif part.function_call:
                        name = part.function_call.name
                        if not name:
                            raise ValueError("Tool call name is required")
                        # Google's args are already a dict
                        args = part.function_call.args

                        tool_call = ToolCall(
                            id=str(
                                uuid4()
                            ),  # Generate a unique ID as Google doesn't provide one
                            name=name,
                            arguments=args,
                        )
                        content_blocks.append(tool_call)

        return ParsedResponseCandidate(
            content_blocks=content_blocks,
            metadata=ResponseMetadata(
                normalized_finish_reason=stop_reason, raw_finish_reason=finish_reason
            ),
        )

    @classmethod
    def parse_response(
        cls, response: GoogleGenerateContentResponse, provider: Provider
    ) -> ParsedResponse:
        """Parse a Google response into a normalized format."""
        # Ensure we have candidates
        if not response.candidates:
            return ParsedResponse(
                provider=provider,
                candidates=[],
                stop_reason=StopReason.ERROR,
                raw_response=response.model_dump(by_alias=True, mode="json"),
            )

        # Parse each candidate
        parsed_candidates = [
            cls.parse_candidate(candidate) for candidate in response.candidates
        ]

        # Extract token usage including thinking tokens
        usage_metadata = response.usage_metadata
        if usage_metadata:
            prompt_tokens = usage_metadata.prompt_token_count or 0
            completion_tokens = usage_metadata.candidates_token_count or 0
            # Check for thoughts_token_count (Gemini 2.5+)
            thinking_tokens = getattr(usage_metadata, "thoughts_token_count", None)

            usage = TokenUsage(
                input_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                thinking_tokens=thinking_tokens,
            )
        else:
            usage = TokenUsage()
        model = response.model_version

        return ParsedResponse(
            provider=provider,
            candidates=parsed_candidates,
            stop_reason=parsed_candidates[0].metadata.normalized_finish_reason,
            usage=usage,
            model=model,
            raw_response=response.model_dump(by_alias=True, mode="json"),
        )

    @classmethod
    def extract_metadata(
        cls, response: GoogleGenerateContentResponse
    ) -> dict[str, Any]:
        """Extract additional metadata from Google response."""
        metadata = {}

        # Add safety ratings if available
        if response.candidates:
            candidate = response.candidates[0]
            if candidate.safety_ratings:
                metadata["safety_ratings"] = candidate.safety_ratings

        return metadata


class ResponseParserOpenAIResponses(
    ResponseParserProtocol[OpenAIResponse, ParsedResponse]
):
    """Parser for OpenAI Responses API responses."""

    @staticmethod
    def parse_output_items(output: list) -> ParsedResponseCandidate:
        """Parse output items into a single candidate.

        Note: Responses API returns a single response with multiple output items,
        not multiple choices/candidates like Chat API. Order is preserved as the
        output array order indicates execution sequence.
        """
        content_blocks: list[TextContent | ToolCall | ThinkingContent | ReasoningContent] = []

        # Process each output item in order (order matters for reasoning -> message flow)
        for item in output:
            item_type = getattr(item, "type", None)

            if item_type == "reasoning":
                # Reasoning output item (o1/o3 models with Responses API)
                summary = getattr(item, "summary", [])
                if summary:
                    # summary is a list of summary items, extract text from summary_text items
                    texts = []
                    for s in summary:
                        if isinstance(s, dict) and s.get("type") == "summary_text":
                            texts.append(s.get("text", ""))
                        elif hasattr(s, "type") and s.type == "summary_text":
                            texts.append(getattr(s, "text", ""))
                    if texts:
                        content_blocks.append(ReasoningContent(summary="".join(texts)))

            elif item_type == "message":
                # ResponseOutputMessage - extract text content
                if hasattr(item, "content"):
                    for content_item in item.content:
                        content_type = getattr(content_item, "type", None)
                        if content_type == "output_text":
                            text = getattr(content_item, "text", "")
                            content_blocks.append(TextContent(text=text))

            elif item_type == "function_call":
                # ResponseFunctionToolCall
                call_id = getattr(item, "call_id", "")
                name = getattr(item, "name", "")
                arguments_str = getattr(item, "arguments", "{}")

                # Parse arguments from JSON string
                try:
                    args_dict = (
                        json.loads(arguments_str)
                        if isinstance(arguments_str, str)
                        else arguments_str
                    )
                except json.JSONDecodeError:
                    args_dict = {"raw_arguments": arguments_str}

                content_blocks.append(
                    ToolCall(id=call_id, name=name, arguments=args_dict)
                )

        # Default stop reason - will be updated from Response.status
        stop_reason = StopReason.END_TURN

        return ParsedResponseCandidate(
            content_blocks=content_blocks,
            metadata=ResponseMetadata(
                normalized_finish_reason=stop_reason,
                raw_finish_reason="completed",
            ),
        )

    @classmethod
    def parse_response(
        cls, response: OpenAIResponse, provider: Provider
    ) -> ParsedResponse:
        """Parse an OpenAI Responses API response into normalized format."""
        # Parse the single output array (not multiple choices)
        candidate = cls.parse_output_items(response.output)

        # Map status to stop reason
        status = getattr(response, "status", "completed")
        if status == "completed":
            stop_reason = StopReason.END_TURN
        elif status == "incomplete":
            # Check incomplete details for more specific reason
            incomplete_details = getattr(response, "incomplete_details", None)
            if incomplete_details:
                reason = getattr(incomplete_details, "reason", None)
                if reason == "max_output_tokens":
                    stop_reason = StopReason.MAX_TOKENS
                elif reason == "content_filter":
                    stop_reason = StopReason.CONTENT_FILTER
                else:
                    stop_reason = StopReason.OTHER
            else:
                stop_reason = StopReason.OTHER
        elif status == "failed":
            stop_reason = StopReason.ERROR
        else:
            stop_reason = StopReason.OTHER

        # Update candidate metadata with actual status
        candidate.metadata.normalized_finish_reason = stop_reason
        candidate.metadata.raw_finish_reason = status

        # Extract token usage including reasoning tokens
        usage_obj = getattr(response, "usage", None)
        thinking_tokens = None
        if usage_obj:
            # Check for reasoning_tokens in output_tokens_details (o-series, GPT-5)
            output_details = getattr(usage_obj, "output_tokens_details", None)
            if output_details:
                thinking_tokens = getattr(output_details, "reasoning_tokens", None)
        usage = TokenUsage(
            input_tokens=getattr(usage_obj, "input_tokens", None)
            if usage_obj
            else None,
            completion_tokens=getattr(usage_obj, "output_tokens", None)
            if usage_obj
            else None,
            thinking_tokens=thinking_tokens,
        )

        return ParsedResponse(
            provider=provider,
            candidates=[candidate],  # Single candidate (no n parameter)
            stop_reason=stop_reason,
            usage=usage,
            model=response.model,
            raw_response=response.model_dump(by_alias=True, mode="json")
            if hasattr(response, "model_dump")
            else {},
        )

    @classmethod
    def extract_metadata(cls, response: OpenAIResponse) -> dict[str, Any]:
        """Extract OpenAI Responses API specific metadata."""
        metadata = {}
        if hasattr(response, "id"):
            metadata["openai_response_id"] = response.id
        return metadata


class ResponseParser:
    """
    Factory class to parse LLM responses based on provider type.

    Handles normalization of responses from different providers into
    a consistent ParsedResponse format.
    """

    _parsers: ClassVar[dict[Provider, Type[ResponseParserProtocol]]] = {
        Provider.ANTHROPIC: ResponseParserAnthropic,
        Provider.OPENAI_CHAT: ResponseParserOpenAI,
        Provider.OPENAI_RESPONSES: ResponseParserOpenAIResponses,
        Provider.GOOGLE_GEMINI: ResponseParserGoogle,
        Provider.GOOGLE_VERTEX: ResponseParserGoogle,
    }

    @classmethod
    def get_parser(cls, provider: Provider) -> ResponseParserProtocol:
        """Get the parser for a given provider."""
        if provider == Provider.ANTHROPIC:
            return cls._parsers[Provider.ANTHROPIC]
        elif provider == Provider.OPENAI_CHAT:
            return cls._parsers[Provider.OPENAI_CHAT]
        elif provider == Provider.OPENAI_RESPONSES:
            return cls._parsers[Provider.OPENAI_RESPONSES]
        elif provider == Provider.GOOGLE_GEMINI:
            return cls._parsers[Provider.GOOGLE_GEMINI]
        elif provider == Provider.GOOGLE_VERTEX:
            return cls._parsers[Provider.GOOGLE_VERTEX]
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    @classmethod
    @overload
    def parse(
        cls, response: AnthropicMessage, provider: Literal[Provider.ANTHROPIC]
    ) -> ParsedResponse: ...

    @classmethod
    @overload
    def parse(
        cls, response: OpenAIChatCompletion, provider: Literal[Provider.OPENAI_CHAT]
    ) -> ParsedResponse: ...

    @classmethod
    @overload
    def parse(
        cls, response: OpenAIResponse, provider: Literal[Provider.OPENAI_RESPONSES]
    ) -> ParsedResponse: ...

    @classmethod
    @overload
    def parse(
        cls,
        response: GoogleGenerateContentResponse,
        provider: Literal[Provider.GOOGLE_GEMINI],
    ) -> ParsedResponse: ...

    @classmethod
    @overload
    def parse(
        cls,
        response: GoogleGenerateContentResponse,
        provider: Literal[Provider.GOOGLE_VERTEX],
    ) -> ParsedResponse: ...

    @classmethod
    def parse(
        cls,
        response: AnthropicMessage
        | OpenAIChatCompletion
        | OpenAIResponse
        | GoogleGenerateContentResponse,
        provider: Provider,
    ) -> ParsedResponse:
        """
        Parse an LLM response based on provider type.

        Args:
            response: The raw response from the provider
            provider: The provider type

        Returns:
            A normalized ParsedResponse object
        """
        if provider not in cls._parsers:
            raise ValueError(f"Unsupported provider: {provider}")

        parser = cls._parsers[provider]
        return parser.parse_response(response, provider)


class ResponseMetadataExtractor:
    """Utility class to extract and format response metadata for telemetry."""

    @staticmethod
    def extract_for_telemetry(parsed_response: ParsedResponse) -> dict[str, Any]:
        """
        Extract metadata from a parsed response for telemetry purposes.

        Args:
            parsed_response: The normalized parsed response

        Returns:
            A dictionary of metadata suitable for telemetry
        """
        metadata = {
            "provider": parsed_response.provider.value,
            "model": parsed_response.model,
            "stop_reason": parsed_response.stop_reason.value,
            "usage": parsed_response.usage.model_dump(by_alias=True),
        }

        return metadata


class ResponseTypeDetector:
    """Utility class for detecting and classifying LLM response types.

    Analyzes parsed responses and request configurations to determine
    the type of response for observability and UI rendering purposes.
    """

    @staticmethod
    def detect(
        parsed_response: ParsedResponse, request_config: RequestConfig | None = None
    ) -> ResponseType:
        """Detect the response type based on content and configuration.

        Args:
            parsed_response: The parsed LLM response
            request_config: Optional request configuration used for the call

        Returns:
            ResponseType enum value indicating the type of response
        """
        # Check if structured generation was requested
        is_structured = ResponseTypeDetector._is_structured_generation(request_config)

        # Analyze content blocks to determine presence of text, tool calls, and thinking
        has_text = False
        has_tool_calls = False
        has_thinking = False

        for candidate in parsed_response.candidates:
            for block in candidate.content_blocks:
                if isinstance(block, TextContent):
                    has_text = True
                elif isinstance(block, ToolCall):
                    has_tool_calls = True
                elif isinstance(block, (ThinkingContent, ReasoningContent)):
                    has_thinking = True

        # Classify based on content and configuration
        if is_structured:
            if has_tool_calls:
                return ResponseType.STRUCTURED_WITH_TOOLS
            else:
                return ResponseType.STRUCTURED

        # Thinking-aware classification (takes precedence over text-only)
        if has_thinking:
            if has_tool_calls:
                return ResponseType.THINKING_WITH_TOOLS
            elif has_text:
                return ResponseType.TEXT_WITH_THINKING
            else:
                return ResponseType.THINKING

        # Standard classification
        if has_text and has_tool_calls:
            return ResponseType.TEXT_WITH_TOOLS
        elif has_tool_calls:
            return ResponseType.TOOL_CALLS
        else:
            return ResponseType.TEXT

    @staticmethod
    def _is_structured_generation(request_config: RequestConfig | None) -> bool:
        """Check if the request was configured for structured generation.

        Args:
            request_config: The request configuration to check

        Returns:
            True if structured generation was configured, False otherwise
        """
        if request_config is None:
            return False

        # Check provider-specific structured generation indicators
        if hasattr(request_config, "response_format"):
            # OpenAI Chat API structured outputs
            response_format = request_config.response_format
            if isinstance(response_format, dict):
                format_type = response_format.get("type")
                if format_type in ("json_object", "json_schema"):
                    return True

        if hasattr(request_config, "response_schema"):
            # Google structured generation
            if request_config.response_schema is not None:
                return True

        if hasattr(request_config, "response_mime_type"):
            # Google JSON mode
            if request_config.response_mime_type == "application/json":
                return True

        return False

    @staticmethod
    def count_tool_calls(parsed_response: ParsedResponse) -> int:
        """Count the total number of tool calls across all candidates.

        Args:
            parsed_response: The parsed LLM response

        Returns:
            Total count of tool calls in the response
        """
        count = 0
        for candidate in parsed_response.candidates:
            for block in candidate.content_blocks:
                if isinstance(block, ToolCall):
                    count += 1
        return count


class LLMEvent(LLMEventModelBase[ParsedResponse, Message]):
    """Domain model for LLM interactions"""

    messages: list[Message] = Field(..., alias="messages")
    parsed_response: ParsedResponse = Field(..., alias="parsedResponse")


# Rebuild the model to resolve forward references from the base class
# (RequestConfig, SchemaDefinition, etc. are TYPE_CHECKING imports in moxn.types)
from typing import Optional  # noqa: E402, F811

from moxn.types.request_config import RequestConfig, SchemaDefinition  # noqa: E402

LLMEvent.model_rebuild(_types_namespace={"Optional": Optional, "RequestConfig": RequestConfig, "SchemaDefinition": SchemaDefinition})
