"""Tool types for function calling and structured generation.

These types represent tools attached to prompts, which can be either:
- Function calling tools (toolType='tool')
- Structured output schemas (toolType='structured_output')
"""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from moxn.types.base import GitTrackedEntity


class SdkSchema(GitTrackedEntity):
    """Schema definition for a tool or structured output.

    Contains the compiled JSON Schema that defines the tool's parameters
    or the structured output format.
    """

    id: UUID
    name: str
    description: str | None = None
    exported_json: str = Field(
        ...,
        alias="exportedJSON",
        description="Compiled JSON Schema as a string",
    )

    model_config = ConfigDict(populate_by_name=True)


class SdkTool(BaseModel):
    """Tool attached to a prompt for function calling or structured output.

    Tools are stored in the prompt's tools array and can be either:
    - Function calling tools (tool_type='tool'): Allow the LLM to invoke functions
    - Structured output schemas (tool_type='structured_output'): Define response format

    The schema contains the full JSON Schema definition - no additional fetching
    is required at invocation time.
    """

    schema_: SdkSchema = Field(
        ...,
        alias="schema",
        description="The full schema definition for this tool",
    )
    tool_type: Literal["tool", "structured_output"] = Field(
        ...,
        alias="toolType",
        description="Whether this is a function calling tool or structured output schema",
    )
    position: int = Field(
        ...,
        description="Order in the tool list (0-indexed)",
    )
    is_required: bool = Field(
        ...,
        alias="isRequired",
        description="Whether this tool must be called (for 'tool' type)",
    )

    model_config = ConfigDict(populate_by_name=True)
