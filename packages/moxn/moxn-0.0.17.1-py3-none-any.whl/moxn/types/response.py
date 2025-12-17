"""
Module for parsing and normalizing LLM responses across different providers.
"""

from enum import Enum
from typing import (
    Any,
    Generic,
    Protocol,
    TypeVar,
)
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from moxn.types.blocks.text import (
    ReasoningContentModel,
    TextContentModel,
    ThinkingContentModel,
)
from moxn.types.blocks.tool import ToolCallModel
from moxn.types.content import Provider


class StopReason(str, Enum):
    """Normalized stop reasons across providers."""

    END_TURN = "end_turn"  # Normal completion
    MAX_TOKENS = "max_tokens"  # Max tokens reached
    TOOL_CALL = "tool_call"  # Model wants to call a tool
    CONTENT_FILTER = "content_filter"  # Content was filtered for safety reasons
    ERROR = "error"  # Some error occurred
    OTHER = "other"  # Other reason


class TokenUsage(BaseModel):
    """Normalized token usage across providers."""

    input_tokens: int | None = Field(default=None, alias="inputTokens")
    thinking_tokens: int | None = Field(default=None, alias="thinkingTokens")
    completion_tokens: int | None = Field(default=None, alias="completionTokens")

    model_config = ConfigDict(populate_by_name=True)


class ResponseMetadata(BaseModel):
    """Normalized response metadata across providers."""

    normalized_finish_reason: StopReason = Field(
        ..., alias="normalizedFinishReason"
    )
    raw_finish_reason: str = Field(..., alias="rawFinishReason")

    model_config = ConfigDict(populate_by_name=True)


# Generic type parameters for content blocks
TextContentT = TypeVar("TextContentT", bound=TextContentModel, covariant=True)
ToolCallT = TypeVar("ToolCallT", bound=ToolCallModel, covariant=True)
ThinkingContentT = TypeVar(
    "ThinkingContentT", bound=ThinkingContentModel, covariant=True
)
ReasoningContentT = TypeVar(
    "ReasoningContentT", bound=ReasoningContentModel, covariant=True
)


class ParsedResponseCandidateModelBase(
    BaseModel, Generic[TextContentT, ToolCallT, ThinkingContentT, ReasoningContentT]
):
    """Normalized response candidate with ordered content blocks and metadata.

    Content blocks preserve the order from the provider response, which is important
    for interleaved thinking/text/tool_call sequences in extended thinking models.
    """

    model_config = ConfigDict(populate_by_name=True)

    content_blocks: list[TextContentT | ToolCallT | ThinkingContentT | ReasoningContentT] = Field(
        alias="contentBlocks"
    )
    metadata: ResponseMetadata


class ParsedResponseCandidateModel(
    ParsedResponseCandidateModelBase[
        TextContentModel, ToolCallModel, ThinkingContentModel, ReasoningContentModel
    ]
):
    """Normalized response candidate with content blocks and metadata."""

    content_blocks: list[
        TextContentModel | ToolCallModel | ThinkingContentModel | ReasoningContentModel
    ] = Field(alias="contentBlocks")
    metadata: ResponseMetadata


ParsedResponseCandidateModelT = TypeVar(
    "ParsedResponseCandidateModelT", bound=ParsedResponseCandidateModelBase
)


class ParsedResponseModelBase(BaseModel, Generic[ParsedResponseCandidateModelT]):
    """
    Normalized response content from any LLM provider.

    Contains parsed content blocks, metadata, and original response for reference.
    """

    id: UUID = Field(default_factory=uuid4)
    provider: Provider
    candidates: list[ParsedResponseCandidateModelT]
    stop_reason: StopReason = Field(
        ...,
        alias="stopReason",
        description="Normalized stop reason - from first candidate if multiple candidates",
    )
    usage: TokenUsage = Field(
        default_factory=TokenUsage,
        description="Token usage from parent objects, candidate token usage in candidate metadata if available",
    )
    model: str | None = None
    raw_response: dict | None = Field(default=None, alias="rawResponse")

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)


ResponseType = TypeVar("ResponseType", contravariant=True)
ParsedResponseModelT = TypeVar(
    "ParsedResponseModelT", bound=ParsedResponseModelBase, covariant=True
)


class ResponseParserProtocol(Protocol, Generic[ResponseType, ParsedResponseModelT]):
    """Protocol for provider-specific response parsers."""

    @classmethod
    def parse_response(
        cls, response: ResponseType, provider: Provider
    ) -> ParsedResponseModelT: ...

    @classmethod
    def extract_metadata(cls, response: ResponseType) -> dict[str, Any]: ...
