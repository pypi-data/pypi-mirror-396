"""Utility functions for provider adapters."""

from typing import Any, Sequence


def convert_blocks_to_document(
    blocks: Sequence[Sequence[Any]],
    provider: Any,
    context: Any,
) -> Sequence[Sequence[Any]]:
    """Convert blocks to provider-specific document, handling variable expansions.

    This helper handles the case where variables might return either:
    - A single content block
    - A list of content blocks (for complex multimodal content)

    Args:
        blocks: The blocks to convert
        provider: The provider to convert for
        context: The message context

    Returns:
        Provider-specific document with properly flattened blocks
    """
    document = []
    for block_group in blocks:
        converted_group = []
        for block in block_group:
            result = block.to_provider_content_block(provider, context)
            # Handle both single blocks and lists of blocks (from variables)
            if isinstance(result, list):
                converted_group.extend(result)
            else:
                converted_group.append(result)
        document.append(converted_group)
    return document
