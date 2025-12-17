from typing import Annotated, Sequence

from pydantic import Field, TypeAdapter

from moxn.base_models.blocks.file import PDFContentFromSource
from moxn.base_models.blocks.image import ImageContentFromSource
from moxn.base_models.blocks.signed import (
    SignedURLContent,
    SignedURLImageContent,
    SignedURLPDFContent,
)
from moxn.base_models.blocks.text import ReasoningContent, TextContent, ThinkingContent
from moxn.base_models.blocks.tool import ToolCall, ToolResult
from moxn.base_models.blocks.variable import Variable

# API ContentBlock - blocks that come from API responses (can be discriminated by block_type)
APIContentBlock = Annotated[
    TextContent
    | ImageContentFromSource
    | PDFContentFromSource
    | SignedURLContent
    | Variable
    | ToolCall
    | ToolResult
    | ThinkingContent
    | ReasoningContent,
    Field(discriminator="block_type"),
]

# Runtime ContentBlock - includes SignedURL types for URL refresh management
RuntimeContentBlock = (
    TextContent
    | ImageContentFromSource
    | PDFContentFromSource
    | SignedURLContent
    | SignedURLImageContent
    | SignedURLPDFContent
    | Variable
    | ToolCall
    | ToolResult
    | ThinkingContent
    | ReasoningContent
)

# Default to API ContentBlock for deserialization
ContentBlock = APIContentBlock

ContentBlockList = Sequence[ContentBlock]
ContentBlockDocument = Sequence[Sequence[ContentBlock]]

ContentBlockAdapter: TypeAdapter[ContentBlock] = TypeAdapter(ContentBlock)
