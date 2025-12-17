"""Type definitions for OpenAI Responses API provider-specific content blocks."""

from typing import TYPE_CHECKING, Sequence, TypedDict, Union

if TYPE_CHECKING:
    # Import from openai SDK - Responses API types
    from openai.types.responses import Response as OpenAIResponse
    from openai.types.responses import (
        ResponseFunctionToolCallParam as OpenAIResponsesFunctionToolCallParam,
    )
    from openai.types.responses import (
        ResponseInputContentParam as OpenAIResponsesInputContent,
    )
    from openai.types.responses import (
        ResponseInputFileParam as OpenAIResponsesInputFileParam,
    )
    from openai.types.responses import (
        ResponseInputImageParam as OpenAIResponsesInputImageParam,
    )
    from openai.types.responses import (
        ResponseInputItemParam as OpenAIResponsesInputItemParam,
    )
    from openai.types.responses import ResponseInputParam as OpenAIResponsesInputParam
    from openai.types.responses import (
        ResponseInputTextParam as OpenAIResponsesInputTextParam,
    )
    from openai.types.responses import ResponseOutputItem as OpenAIResponsesOutputItem
    from openai.types.responses import (
        ResponseOutputMessage as OpenAIResponsesOutputMessage,
    )
    from openai.types.responses.response_input_item_param import (
        FunctionCallOutput as OpenAIResponsesFunctionCallOutput,
    )
    from openai.types.responses.response_input_item_param import (
        Message as OpenAIResponsesMessageItemParam,
    )
else:
    # Runtime fallbacks when OpenAI SDK not installed
    OpenAIResponse = dict
    OpenAIResponsesInputContent = dict
    OpenAIResponsesInputItemParam = dict
    OpenAIResponsesInputParam = list
    OpenAIResponsesInputTextParam = dict
    OpenAIResponsesInputImageParam = dict
    OpenAIResponsesInputFileParam = dict
    OpenAIResponsesFunctionToolCallParam = dict
    OpenAIResponsesFunctionCallOutput = dict
    OpenAIResponsesMessageItemParam = dict
    OpenAIResponsesInputItemParam = dict
    OpenAIResponsesOutputItem = dict
    OpenAIResponsesOutputMessage = dict
    try:
        from openai.types.responses import Response as OpenAIResponse
    except ImportError:
        pass

# Content block types (within Message items and as separate items)
OpenAIResponsesContentBlock = Union[
    OpenAIResponsesInputTextParam,
    OpenAIResponsesInputImageParam,
    OpenAIResponsesInputFileParam,
    OpenAIResponsesFunctionToolCallParam,
    OpenAIResponsesFunctionCallOutput,
]

# Provider-specific block sequences (for document operations)
OpenAIResponsesContentBlockSequence = Sequence[Sequence[OpenAIResponsesContentBlock]]

# Item-level sequences (for items that can be in input/output arrays)
OpenAIResponsesInputItemSequence = Sequence[OpenAIResponsesInputItemParam]


class OpenAIResponsesMessagesParam(TypedDict, total=False):
    """Payload structure for OpenAI Responses API.

    This matches the structure of ResponseCreateParams from the OpenAI SDK,
    but only includes the fields we generate (input and instructions).
    """

    input: list[OpenAIResponsesInputItemParam]
    """List of input items (messages, tool calls, tool results, etc.)."""

    instructions: str
    """System/developer instructions extracted from system-role messages."""
