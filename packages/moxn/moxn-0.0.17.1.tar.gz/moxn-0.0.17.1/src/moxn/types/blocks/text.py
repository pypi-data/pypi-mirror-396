from typing import Literal

from pydantic import ConfigDict, Field

from moxn.types.blocks.base import BaseContent, BlockType


class TextContentModel(BaseContent):
    block_type: Literal[BlockType.TEXT] = Field(
        default=BlockType.TEXT, alias="blockType"
    )
    text: str

    model_config = ConfigDict(populate_by_name=True)


class ThinkingContentModel(BaseContent):
    """Base model for thinking/reasoning content blocks from extended thinking models.

    Used for Claude's extended thinking and Gemini's thinking parts.
    The thinking field contains "[REDACTED]" for redacted thinking blocks.
    """

    block_type: Literal[BlockType.THINKING] = Field(
        default=BlockType.THINKING, alias="blockType"
    )
    thinking: str

    model_config = ConfigDict(populate_by_name=True)


class ReasoningContentModel(BaseContent):
    """Base model for OpenAI reasoning/summary content from o1/o3 models.

    Contains the reasoning summary provided by reasoning models.
    """

    block_type: Literal[BlockType.REASONING] = Field(
        default=BlockType.REASONING, alias="blockType"
    )
    summary: str

    model_config = ConfigDict(populate_by_name=True)
