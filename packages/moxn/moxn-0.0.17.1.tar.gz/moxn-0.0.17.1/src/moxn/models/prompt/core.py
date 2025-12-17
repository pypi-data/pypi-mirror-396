from typing import TYPE_CHECKING, Any, Sequence

from pydantic import Field

from moxn.models import message as msg
from moxn.models import schema as sch
from moxn.types.base import BasePrompt, RenderableModel
from moxn.types.content import MessageRole
from moxn.types.tool import SdkSchema, SdkTool

if TYPE_CHECKING:
    PromptSession = Any


class PromptTemplate(BasePrompt[msg.Message, sch.Schema]):
    """Immutable representation of a stored prompt configuration.

    Prompts can have attached tools for function calling and/or structured output.
    Tools are stored in the `tools` field (inherited from BasePrompt) and can be:
    - Function calling tools (tool_type='tool')
    - Structured output schemas (tool_type='structured_output')
    """

    messages: Sequence[msg.Message]
    input_schema: sch.Schema = Field(..., alias="inputSchema")

    @property
    def function_tools(self) -> list[SdkTool]:
        """Get tools for function calling (tool_type='tool' only).

        Returns:
            List of SdkTool objects that are function calling tools,
            sorted by position.
        """
        if not self.tools:
            return []
        return sorted(
            [t for t in self.tools if t.tool_type == "tool"],
            key=lambda t: t.position,
        )

    @property
    def structured_output_schema(self) -> SdkSchema | None:
        """Get the structured output schema if response_schema_id is set.

        Looks up the schema in the tools array by ID - no fetch, all data is local.
        The schema is only returned if:
        1. completion_config.response_schema_id is set
        2. A matching tool with tool_type='structured_output' exists

        Returns:
            SdkSchema for structured output, or None if not configured.
        """
        if not self.completion_config or not self.completion_config.response_schema_id:
            return None

        if not self.tools:
            return None

        response_schema_id = self.completion_config.response_schema_id
        for tool in self.tools:
            if (
                tool.tool_type == "structured_output"
                and str(tool.schema_.id) == response_schema_id
            ):
                return tool.schema_

        return None

    def get_tool_by_name(self, name: str) -> SdkTool | None:
        """Lookup a tool by name.

        Args:
            name: The name of the tool (matches schema.name)

        Returns:
            SdkTool if found, None otherwise.
        """
        if not self.tools:
            return None

        for tool in self.tools:
            if tool.schema_.name == name:
                return tool

        return None

    def get_messages(self):
        return [message.model_copy(deep=True) for message in self.messages]

    def get_message_by_role(self, role: str | MessageRole) -> msg.Message | None:
        """Get the first message with the specified role."""
        _role = MessageRole(role) if isinstance(role, str) else role

        messages = [p for p in self.messages if p.role == role]
        if len(messages) == 1:
            return messages[0]
        elif len(messages) == 0:
            return None
        else:
            raise ValueError(
                f"get message is not deterministic, there are {len(messages)} {_role.value} messages in the prompt"
            )

    def get_messages_by_role(self, role: str | MessageRole) -> list[msg.Message]:
        """Get all messages with the specified role."""
        role = MessageRole(role) if isinstance(role, str) else role
        return [p for p in self.messages if p.role == role]

    def to_prompt_session(
        self,
        session_data: RenderableModel | None = None,
        render_kwargs: dict[str, Any] | None = None,
    ) -> "PromptSession":  # type: ignore
        from moxn.models.prompt.session import PromptSession

        return PromptSession.from_prompt_template(
            prompt=self,
            session_data=session_data,
            render_kwargs=render_kwargs,
        )
