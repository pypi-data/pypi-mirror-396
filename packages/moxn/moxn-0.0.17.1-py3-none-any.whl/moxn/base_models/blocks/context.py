from typing import TYPE_CHECKING, Any, Literal, Sequence, cast, overload

from moxn.types.blocks.context import MessageContextModel
from moxn.types.blocks.variable import VariableType

# Import types conditionally to avoid circular imports
if TYPE_CHECKING:
    from moxn.base_models.blocks.file import PDFContentFromSource
    from moxn.base_models.blocks.image import ImageContentFromSource
    from moxn.base_models import ContentBlock
else:
    PDFContentFromSource = None
    ImageContentFromSource = None
    ContentBlock = None


class MessageContext(MessageContextModel):
    """Context object that gets passed down from prompt instance to messages to blocks."""

    @overload
    def get_variable(
        self,
        name: str,
        variable_type: Literal[VariableType.PRIMITIVE],
        default: str | int | float | bool | None = None,
    ) -> "str | ContentBlock | Sequence[ContentBlock] | None":
        """Get a primitive variable value by name.

        Returns:
            - str: For string values (backward compatible)
            - ContentBlock: For single content block
            - Sequence[ContentBlock]: For multiple content blocks
            - None: If variable not found and no default
        """
        pass

    @overload
    def get_variable(
        self, name: str, variable_type: Literal[VariableType.IMAGE], default: Any = None
    ) -> "ImageContentFromSource | None":
        """Get an image variable value by name."""
        pass

    @overload
    def get_variable(
        self,
        name: str,
        variable_type: Literal[VariableType.FILE],
        default: Any = None,
    ) -> "PDFContentFromSource | None":
        """Get a document variable value by name."""
        pass

    def get_variable(
        self, name: str, variable_type: VariableType, default: Any = None
    ) -> "str | ContentBlock | Sequence[ContentBlock] | ImageContentFromSource | PDFContentFromSource | None":
        """Get a variable value by name.

        For PRIMITIVE variables:
        - Returns the value as-is if it's a string, ContentBlock, or list[ContentBlock]
        - Converts other types to strings for backward compatibility

        For IMAGE/FILE variables:
        - Returns the specific content type
        """
        variable = self.variables.get(name, default)
        if variable is None:
            return None

        if variable_type == VariableType.PRIMITIVE:
            # Check if it's a content block by checking for the required method
            if hasattr(variable, "_to_anthropic_content_block"):
                # It's a ContentBlock
                return variable
            elif isinstance(variable, (list, tuple)) and all(
                hasattr(v, "_to_anthropic_content_block") for v in variable
            ):
                # It's a list of ContentBlocks
                return variable
            else:
                # Convert to string for backward compatibility
                return str(variable)
        elif variable_type == VariableType.IMAGE:
            return cast(ImageContentFromSource, variable)
        elif variable_type == VariableType.FILE:
            return cast(PDFContentFromSource, variable)
        else:
            raise ValueError(f"Unsupported variable type: {variable_type}")

    def get_provider_setting(self, setting_name: str, default: Any = None) -> Any:
        """Get a setting for the active provider."""
        if not self.provider or self.provider not in self.provider_settings:
            return default
        return self.provider_settings[self.provider].get(setting_name, default)

    def has_variable(self, name: str) -> bool:
        """Check if a variable exists."""
        return name in self.variables

    @classmethod
    def create_empty(cls) -> "MessageContext":
        """Create an empty context."""
        return cls()

    @classmethod
    def from_variables(cls, variables: dict[str, Any]) -> "MessageContext":
        """Create a context initialized with variables.

        Variables can be:
        - str, int, float, bool: Will be converted to strings when used
        - ContentBlock: Single content block
        - Sequence[ContentBlock]: Multiple content blocks
        - ImageContentFromSource/PDFContentFromSource: Multimodal content
        """
        return cls(variables=variables)

    def merge(self, other: "MessageContext | dict | None") -> "MessageContext":
        """Merge another context into this one, with the other context taking precedence.

        Args:
            other: Another MessageContext or dict of variables to merge.
                   Values from 'other' will override values in self.

        Returns:
            A new MessageContext with merged values.
        """
        if other is None:
            return self.model_copy(deep=True)

        if isinstance(other, dict):
            # If other is a dict, treat it as variables only
            merged_variables = {**self.variables, **other}
            return self.model_copy(update={"variables": merged_variables})

        # Merge all fields, with other taking precedence
        merged_variables = {**self.variables, **other.variables}

        # Merge provider settings deeply
        merged_provider_settings = dict(self.provider_settings)
        for provider, settings in other.provider_settings.items():
            if provider in merged_provider_settings:
                # Merge settings for this provider
                existing = merged_provider_settings[provider]
                if isinstance(existing, dict) and isinstance(settings, dict):
                    merged_provider_settings[provider] = {**existing, **settings}
                else:
                    merged_provider_settings[provider] = settings
            else:
                merged_provider_settings[provider] = settings

        # Merge metadata
        merged_metadata = {**self.metadata, **other.metadata}

        return self.model_copy(
            update={
                "provider": other.provider or self.provider,
                "variables": merged_variables,
                "provider_settings": merged_provider_settings,
                "metadata": merged_metadata,
            }
        )
