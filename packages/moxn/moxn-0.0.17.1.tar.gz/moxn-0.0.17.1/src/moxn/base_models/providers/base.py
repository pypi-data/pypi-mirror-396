"""Base protocol for provider adapters."""

from typing import ClassVar, Generic, Protocol, Sequence, TypeVar

from moxn.base_models.blocks.context import MessageContext
from moxn.types.content import Provider

T_MoxnContentBlock = TypeVar("T_MoxnContentBlock", contravariant=True)
T_ProviderContentBlock = TypeVar("T_ProviderContentBlock", covariant=True)
T_ProviderMessage = TypeVar("T_ProviderMessage", covariant=True)


class ProviderAdapter(
    Protocol,
    Generic[
        T_MoxnContentBlock,
        T_ProviderContentBlock,
        T_ProviderMessage,
    ],
):
    """Protocol defining the interface for provider adapters."""

    PROVIDER: ClassVar[Provider]

    @classmethod
    def to_provider_content_document(
        cls,
        blocks: Sequence[Sequence[T_MoxnContentBlock]],
        context: MessageContext,
    ) -> Sequence[Sequence[T_ProviderContentBlock]]:
        """Convert blocks to a provider-specific content document."""
        ...

    @classmethod
    def to_provider_content_blocks(
        cls,
        blocks: Sequence[Sequence[T_MoxnContentBlock]],
        context: MessageContext,
    ) -> Sequence[T_ProviderContentBlock]:
        """Convert Tiptap document tree to flattened provider-specific content blocks."""
        ...

    @classmethod
    def to_message_params(
        cls,
        blocks: Sequence[Sequence[T_MoxnContentBlock]],
        context: MessageContext,
    ) -> Sequence[T_ProviderMessage]:
        """Convert blocks to a provider-specific message parameter."""
        ...
