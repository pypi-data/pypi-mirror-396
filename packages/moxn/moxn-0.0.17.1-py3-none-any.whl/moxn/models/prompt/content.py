from pydantic import BaseModel

from moxn.base_models.blocks.file import (
    PDFContentFromSource,
    PDFContentFromSourceAdapter,
)
from moxn.base_models.blocks.image import (
    ImageContentFromSource,
    ImageContentFromSourceAdapter,
)
from moxn.base_models.blocks.text import TextContent
from moxn.base_models.blocks.tool import ToolCall
from moxn.models import message as msg
from moxn.models.response import ParsedResponse
from moxn.types.content import Author, MessageRole


class PromptContent(BaseModel):
    """Manages message content and provides methods for content manipulation."""

    messages: list[msg.Message]

    def append_message(self, message: msg.Message) -> None:
        """Append a message to the conversation history."""
        self.messages.append(message)

    def append_text(
        self,
        text: str,
        name: str = "",
        description: str = "",
        author=Author.HUMAN,
        role=MessageRole.USER,
    ) -> None:
        blocks = TextContent(text=text)
        new_message = msg.Message(
            branchId=None,
            commitId=None,
            taskId=None,
            name=name,
            description=description,
            author=author,
            role=role,
            blocks=[[blocks]],
        )
        self.messages.append(new_message)

    def append_image(
        self,
        image: ImageContentFromSource | dict,
        name: str = "",
        description: str = "",
        author=Author.HUMAN,
        role=MessageRole.USER,
    ) -> None:
        if isinstance(image, dict):
            _image: ImageContentFromSource = (
                ImageContentFromSourceAdapter.validate_python(image)
            )
        else:
            _image = image

        new_message = msg.Message(
            branchId=None,
            commitId=None,
            taskId=None,
            name=name,
            description=description,
            author=author,
            role=role,
            blocks=[[_image]],
        )
        self.messages.append(new_message)

    def append_file(
        self,
        file: PDFContentFromSource | dict,
        name: str = "",
        description: str = "",
        author=Author.HUMAN,
        role=MessageRole.USER,
    ) -> None:
        if isinstance(file, dict):
            _file: PDFContentFromSource = PDFContentFromSourceAdapter.validate_python(
                file
            )
        else:
            _file = file

        new_message = msg.Message(
            branchId=None,
            commitId=None,
            taskId=None,
            name=name,
            description=description,
            author=author,
            role=role,
            blocks=[[_file]],
        )
        self.messages.append(new_message)

    def append_parsed_response(
        self,
        parsed_response: ParsedResponse,
        candidate_idx: int = 0,
        name: str = "",
        description: str = "",
    ) -> "PromptContent":
        if not parsed_response.candidates:
            raise ValueError("Response contains no candidates")

        if candidate_idx >= len(parsed_response.candidates):
            raise IndexError(
                f"Candidate index {candidate_idx} out of range (0-{len(parsed_response.candidates) - 1})"
            )

        candidate = parsed_response.candidates[candidate_idx]
        blocks: list[list[TextContent | ToolCall]] = []
        current_block_group: list[TextContent | ToolCall] = []

        for content_block in candidate.content_blocks:
            if isinstance(content_block, TextContent):
                current_block_group.append(content_block)
            elif isinstance(content_block, ToolCall):
                if current_block_group:
                    blocks.append(current_block_group)
                    current_block_group = []
                blocks.append([content_block])
            else:
                current_block_group.append(content_block)

        if current_block_group:
            blocks.append(current_block_group)

        new_message = msg.Message(
            branchId=None,
            commitId=None,
            taskId=None,
            name=name,
            description=description,
            author=Author.MACHINE,
            role=MessageRole.ASSISTANT,
            blocks=blocks,
        )

        self.messages.append(new_message)
        return self
