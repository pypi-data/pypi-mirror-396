from typing import Sequence, Union

# Provider payload types (for prompt conversion)
from moxn.types.type_aliases.anthropic import (
    AnthropicContentBlockParam,
    AnthropicMessage,
    AnthropicMessageParam,
    AnthropicMessagesParam,
    AnthropicTextBlockParam,
)
from moxn.types.type_aliases.google import (
    GoogleContent,
    GoogleContentBlock,
    GoogleGenerateContentResponse,
    GoogleMessagesParam,
)
from moxn.types.type_aliases.openai_chat import (
    OpenAIChatAssistantMessageParam,
    OpenAIChatCompletion,
    OpenAIChatContentBlock,
    OpenAIChatMessagesParam,
    OpenAIChatSystemMessageParam,
    OpenAIChatUserMessageParam,
)
from moxn.types.type_aliases.openai_responses import (
    OpenAIResponse,
    OpenAIResponsesContentBlock,
    OpenAIResponsesInputItemParam,
    OpenAIResponsesMessagesParam,
)
from moxn.types.type_aliases.invocation import (
    AnthropicInvocationParam,
    GoogleInvocationParam,
    OpenAIChatInvocationParam,
    OpenAIResponsesInvocationParam,
    ProviderInvocationPayload,
)

# Content block types
ProviderContentBlock = (
    AnthropicContentBlockParam
    | OpenAIChatContentBlock
    | OpenAIResponsesContentBlock
    | GoogleContentBlock
)

ProviderContentBlockSequence = (
    Sequence[Sequence[AnthropicContentBlockParam]]
    | Sequence[Sequence[OpenAIChatContentBlock]]
    | Sequence[Sequence[OpenAIResponsesContentBlock]]
    | Sequence[Sequence[GoogleContentBlock]]
)

# Provider response types (for parsing)
ProviderResponse = Union[
    AnthropicMessage,
    OpenAIChatCompletion,
    OpenAIResponse,
    GoogleGenerateContentResponse,
]

# Provider message param types (for message conversion)
ProviderMessageParam = Union[
    AnthropicTextBlockParam,
    AnthropicMessageParam,
    OpenAIChatSystemMessageParam,
    OpenAIChatUserMessageParam,
    OpenAIChatAssistantMessageParam,
    OpenAIResponsesInputItemParam,  # Properly typed Responses API items
    GoogleContent,
]


ProviderPayload = Union[
    AnthropicMessagesParam,
    OpenAIChatMessagesParam,
    OpenAIResponsesMessagesParam,
    GoogleMessagesParam,
]
