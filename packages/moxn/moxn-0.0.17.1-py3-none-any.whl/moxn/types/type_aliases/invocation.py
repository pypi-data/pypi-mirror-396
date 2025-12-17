"""Combined invocation TypedDicts for direct SDK unpacking.

These TypedDicts combine message payloads with model parameters,
enabling direct unpacking into provider SDK calls:

    response = await anthropic.messages.create(**session.to_anthropic_invocation())
"""

from typing import Sequence, TypedDict

from moxn.types.type_aliases.anthropic import (
    AnthropicContentBlockParam,
    AnthropicSystemContentBlockParam,
)
from moxn.types.type_aliases.google import GoogleContent, GoogleFile
from moxn.types.type_aliases.openai_chat import OpenAIChatContentBlock
from moxn.types.type_aliases.openai_responses import OpenAIResponsesInputItemParam


class AnthropicInvocationParam(TypedDict, total=False):
    """Complete Anthropic payload for `anthropic.messages.create(**payload)`.

    Combines message content with model parameters for direct SDK unpacking.
    """

    # Message fields (from AnthropicMessagesParam)
    system: str | list[AnthropicSystemContentBlockParam]
    messages: list[AnthropicContentBlockParam]

    # Model parameters
    model: str
    max_tokens: int
    temperature: float
    top_p: float

    # Thinking/reasoning parameters
    thinking: dict


class OpenAIChatInvocationParam(TypedDict, total=False):
    """Complete OpenAI Chat payload for `openai.chat.completions.create(**payload)`.

    Combines message content with model parameters for direct SDK unpacking.
    """

    # Message fields (from OpenAIChatMessagesParam)
    messages: list[OpenAIChatContentBlock]

    # Model parameters
    model: str
    max_tokens: int
    temperature: float
    top_p: float

    # Thinking/reasoning parameters
    reasoning_effort: str


class OpenAIResponsesInvocationParam(TypedDict, total=False):
    """Complete OpenAI Responses API payload for `openai.responses.create(**payload)`.

    Combines input items with model parameters for direct SDK unpacking.
    """

    # Message fields (from OpenAIResponsesMessagesParam)
    input: list[OpenAIResponsesInputItemParam]
    instructions: str

    # Model parameters
    model: str
    max_tokens: int
    temperature: float
    top_p: float

    # Thinking/reasoning parameters
    reasoning: dict


class GoogleGenerateContentConfigDict(TypedDict, total=False):
    """Config options for Google genai `generate_content()`.

    These parameters are nested under the `config` key when calling
    `client.models.generate_content(model=..., contents=..., config=...)`.
    """

    # System instruction
    system_instruction: str

    # Generation parameters
    temperature: float
    top_p: float
    top_k: int
    max_output_tokens: int
    stop_sequences: list[str]
    presence_penalty: float
    frequency_penalty: float

    # Tool configuration
    tools: list[dict]
    tool_config: dict

    # Structured output
    response_schema: dict
    response_mime_type: str

    # Thinking/reasoning (for models that support it)
    thinking_config: dict


class GoogleInvocationParam(TypedDict, total=False):
    """Complete Google Gemini/Vertex payload for `generate_content(**payload)`.

    Designed for direct SDK unpacking:
        payload = session.to_google_gemini_invocation()
        response = client.models.generate_content(**payload)

    Note: Google genai SDK uses:
    - `contents` (plural) not `content`
    - Nested `config` for all generation parameters
    """

    # Top-level parameters
    model: str
    contents: Sequence[GoogleContent | GoogleFile]

    # All config params nested here
    config: GoogleGenerateContentConfigDict


# Union type for any provider invocation payload
ProviderInvocationPayload = (
    AnthropicInvocationParam
    | OpenAIChatInvocationParam
    | OpenAIResponsesInvocationParam
    | GoogleInvocationParam
)
