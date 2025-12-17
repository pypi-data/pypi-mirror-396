"""Request models for write operations (creates) shared between SDK and API."""

from typing import Sequence
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from moxn.types.blocks.content_block import ContentBlockModel
from moxn.types.content import Author, MessageRole


class TaskCreateRequest(BaseModel):
    """Request to create a new task."""

    name: str = Field(..., min_length=1, max_length=255, description="Task name")
    description: str | None = Field(
        None, max_length=1000, description="Optional task description"
    )
    branch_name: str = Field(
        "main", alias="branchName", description="Branch to create task on"
    )

    model_config = ConfigDict(populate_by_name=True)


class MessageData(BaseModel):
    """Message data for inline creation within prompts.

    Messages are created as part of prompt creation, not as standalone entities.
    """

    name: str = Field(..., description="Message name")
    role: MessageRole = Field(
        ..., description="Message role (system, user, assistant, etc.)"
    )
    author: Author = Field(
        Author.HUMAN, description="Message author (HUMAN or MACHINE)"
    )
    description: str | None = Field(None, description="Optional message description")
    blocks: Sequence[Sequence[ContentBlockModel]] = Field(
        ..., description="2D array of content blocks (paragraphs containing blocks)"
    )

    model_config = ConfigDict(populate_by_name=True)


class PromptCreateRequest(BaseModel):
    """Request to create a prompt with messages.

    The backend will:
    - Create the prompt
    - Create all messages inline
    - Auto-generate the input schema from variables in messages
    - Handle property deduplication for variables with same name
    """

    name: str = Field(..., min_length=1, max_length=255, description="Prompt name")
    task_id: UUID = Field(..., alias="taskId", description="Parent task ID")
    description: str | None = Field(None, description="Optional prompt description")
    branch_name: str = Field(
        "main", alias="branchName", description="Branch to create prompt on"
    )
    messages: Sequence[MessageData] = Field(
        ..., description="Messages to create with the prompt (at least one required)"
    )

    model_config = ConfigDict(populate_by_name=True)
