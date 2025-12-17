"""Typed domain models for content blocks used in provider conversion."""

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from google.genai.types import File as GoogleFile
else:
    GoogleFile = Any


class BlockType(str, Enum):
    """Content block types."""

    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    VARIABLE = "variable"
    SIGNED = "signed"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


class VariableType(str, Enum):
    """Variable block sub-types."""

    PRIMITIVE = "primitive"
    IMAGE = "image"
    FILE = "file"


class VariableFormat(str, Enum):
    """Variable display format."""

    INLINE = "inline"
    BLOCK = "block"


class ImageSourceType(str, Enum):
    """Image source types."""

    BASE64 = "base64"
    BYTES = "bytes"
    URL = "url"
    LOCAL_FILE = "local_file"
    GOOGLE_FILE = "google_file"
    GOOGLE_FILE_REFERENCE = "google_file_reference"


class FileSourceType(str, Enum):
    """File source types."""

    BASE64 = "base64"
    BYTES = "bytes"
    URL = "url"
    OPENAI_FILE_REFERENCE = "openai_file_reference"
    GOOGLE_FILE = "google_file"
    GOOGLE_FILE_REFERENCE = "google_file_reference"


# Base classes
class TypedBlockBase(BaseModel):
    """Base class for all typed content blocks."""

    block_type: BlockType = Field(alias="blockType")
    options: dict[str, Any] = {}

    model_config = ConfigDict(populate_by_name=True)


# Text Content
class TextContent(TypedBlockBase):
    """Text content block."""

    block_type: BlockType = Field(default=BlockType.TEXT, alias="blockType")
    text: str


# Variable Content
class VariableContent(TypedBlockBase):
    """Variable content block."""

    block_type: BlockType = Field(default=BlockType.VARIABLE, alias="blockType")
    name: str
    variable_type: VariableType = Field(alias="variableType")
    format: VariableFormat
    description: str = ""
    required: bool = True
    default_value: str | None = Field(default=None, alias="defaultValue")


# Image Content
class ImageContent(TypedBlockBase):
    """Image content block."""

    block_type: BlockType = Field(default=BlockType.IMAGE, alias="blockType")
    source_type: ImageSourceType = Field(alias="sourceType")
    media_type: str = Field(alias="mediaType")  # e.g., "image/jpeg", "image/png"

    # Source-specific fields (only one should be populated based on source_type)
    base64: str | None = None
    bytes_data: bytes | None = Field(default=None, alias="bytesData")
    url: str | None = None
    filepath: Path | None = None
    google_file: GoogleFile | None = Field(default=None, alias="googleFile")
    google_uri: str | None = Field(default=None, alias="googleUri")


# File Content
class FileContent(TypedBlockBase):
    """File content block."""

    block_type: BlockType = Field(default=BlockType.FILE, alias="blockType")
    source_type: FileSourceType = Field(alias="sourceType")
    media_type: str = Field(alias="mediaType")  # e.g., "application/pdf"

    # Source-specific fields (only one should be populated based on source_type)
    base64: str | None = None
    bytes_data: bytes | None = Field(default=None, alias="bytesData")
    url: str | None = None
    openai_file_id: str | None = Field(default=None, alias="openaiFileId")
    google_file: GoogleFile | None = Field(default=None, alias="googleFile")
    google_uri: str | None = Field(default=None, alias="googleUri")


# Signed URL Content
class SignedURLContent(TypedBlockBase):
    """Signed URL content block."""

    block_type: BlockType = Field(default=BlockType.SIGNED, alias="blockType")
    file_path: str = Field(alias="filePath")
    media_type: str | None = Field(default=None, alias="mediaType")


# Tool Content (for future extension)
class ToolCallContent(TypedBlockBase):
    """Tool call content block."""

    block_type: BlockType = Field(default=BlockType.TOOL_CALL, alias="blockType")
    tool_name: str = Field(alias="toolName")
    tool_call_id: str = Field(alias="toolCallId")
    arguments: dict[str, Any] = {}


class ToolResultContent(TypedBlockBase):
    """Tool result content block."""

    block_type: BlockType = Field(default=BlockType.TOOL_RESULT, alias="blockType")
    tool_call_id: str = Field(alias="toolCallId")
    result: Any


# Union type for all typed blocks
TypedContentBlock = (
    TextContent
    | VariableContent
    | ImageContent
    | FileContent
    | SignedURLContent
    | ToolCallContent
    | ToolResultContent
)
