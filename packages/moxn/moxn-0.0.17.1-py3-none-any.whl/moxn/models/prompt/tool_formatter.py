"""Tool formatting utilities for converting Moxn tools to provider-specific formats.

This module provides formatters for:
1. ToolFormatter: Converts SdkTool definitions to provider-specific tool formats
2. ToolChoiceTranslator: Translates Moxn tool_choice to provider-specific formats

Provider Translation Reference:

Tool Choice:
| Moxn Value      | OpenAI                                        | Anthropic              | Google                                           |
|-----------------|-----------------------------------------------|------------------------|--------------------------------------------------|
| 'auto'          | 'auto'                                        | {type: 'auto'}         | {mode: 'AUTO'}                                   |
| 'none'          | 'none'                                        | (omit tools)           | {mode: 'NONE'}                                   |
| 'required'      | 'required'                                    | {type: 'any'}          | {mode: 'ANY'}                                    |
| {tool: 'name'}  | {type: 'function', function: {name: 'name'}}  | {type: 'tool', name}   | {mode: 'ANY', allowed_function_names: ['name']}  |

Tool Definition:
| Provider   | Structure                                                           |
|------------|---------------------------------------------------------------------|
| OpenAI     | {type: 'function', function: {name, description, parameters}}       |
| Anthropic  | {name, description, input_schema}                                   |
| Google     | {function_declarations: [{name, description, parameters}]}          |
"""

from __future__ import annotations

import json
from typing import Any

from moxn.types.tool import SdkTool


class ToolFormatter:
    """Converts SdkTool definitions to provider-specific tool formats."""

    @staticmethod
    def to_openai_tools(tools: list[SdkTool]) -> list[dict[str, Any]]:
        """Convert SdkTool list to OpenAI tool format.

        OpenAI format:
        {
            "type": "function",
            "function": {
                "name": "tool_name",
                "description": "Tool description",
                "parameters": { ... JSON Schema ... }
            }
        }

        Args:
            tools: List of SdkTool objects (should be filtered to tool_type='tool')

        Returns:
            List of OpenAI tool definitions
        """
        result = []
        for tool in tools:
            schema = tool.schema_
            parameters = json.loads(schema.exported_json)

            result.append(
                {
                    "type": "function",
                    "function": {
                        "name": schema.name,
                        "description": schema.description or "",
                        "parameters": parameters,
                    },
                }
            )
        return result

    @staticmethod
    def to_anthropic_tools(tools: list[SdkTool]) -> list[dict[str, Any]]:
        """Convert SdkTool list to Anthropic tool format.

        Anthropic format:
        {
            "name": "tool_name",
            "description": "Tool description",
            "input_schema": { ... JSON Schema ... }
        }

        Args:
            tools: List of SdkTool objects (should be filtered to tool_type='tool')

        Returns:
            List of Anthropic tool definitions
        """
        result = []
        for tool in tools:
            schema = tool.schema_
            input_schema = json.loads(schema.exported_json)

            result.append(
                {
                    "name": schema.name,
                    "description": schema.description or "",
                    "input_schema": input_schema,
                }
            )
        return result

    @staticmethod
    def to_google_function_declarations(tools: list[SdkTool]) -> list[dict[str, Any]]:
        """Convert SdkTool list to Google function declarations.

        Google format (function declarations, not wrapped in tools):
        {
            "name": "tool_name",
            "description": "Tool description",
            "parameters": { ... JSON Schema ... }
        }

        Note: Google wraps these in a Tool object with function_declarations array.
        This method returns the declarations; the caller wraps them.

        Args:
            tools: List of SdkTool objects (should be filtered to tool_type='tool')

        Returns:
            List of Google function declarations
        """
        result = []
        for tool in tools:
            schema = tool.schema_
            parameters = json.loads(schema.exported_json)

            result.append(
                {
                    "name": schema.name,
                    "description": schema.description or "",
                    "parameters": parameters,
                }
            )
        return result


class ToolChoiceTranslator:
    """Translates Moxn tool_choice to provider-specific formats."""

    @staticmethod
    def to_openai(choice: str | dict[str, Any]) -> str | dict[str, Any]:
        """Translate Moxn tool_choice to OpenAI format.

        Translations:
        - 'auto' -> 'auto'
        - 'none' -> 'none'
        - 'required' -> 'required'
        - {tool: 'name'} -> {type: 'function', function: {name: 'name'}}

        Args:
            choice: Moxn tool_choice value

        Returns:
            OpenAI tool_choice value
        """
        if isinstance(choice, str):
            # 'auto', 'none', 'required' pass through unchanged
            return choice

        if isinstance(choice, dict) and "tool" in choice:
            # {tool: 'name'} -> {type: 'function', function: {name: 'name'}}
            return {
                "type": "function",
                "function": {"name": choice["tool"]},
            }

        # Pass through any other dict format unchanged
        return choice

    @staticmethod
    def to_anthropic(choice: str | dict[str, Any]) -> dict[str, Any] | None:
        """Translate Moxn tool_choice to Anthropic format.

        Translations:
        - 'auto' -> {type: 'auto'}
        - 'none' -> None (caller should omit tools)
        - 'required' -> {type: 'any'}
        - {tool: 'name'} -> {type: 'tool', name: 'name'}

        Args:
            choice: Moxn tool_choice value

        Returns:
            Anthropic tool_choice value, or None if tools should be omitted
        """
        if isinstance(choice, str):
            if choice == "auto":
                return {"type": "auto"}
            elif choice == "none":
                # Return None to signal that tools should be omitted entirely
                return None
            elif choice == "required":
                return {"type": "any"}
            else:
                # Unknown string, pass through as type
                return {"type": choice}

        if isinstance(choice, dict) and "tool" in choice:
            # {tool: 'name'} -> {type: 'tool', name: 'name'}
            return {"type": "tool", "name": choice["tool"]}

        # Pass through any other dict format unchanged
        return choice

    @staticmethod
    def to_google(choice: str | dict[str, Any]) -> dict[str, Any]:
        """Translate Moxn tool_choice to Google format.

        Translations:
        - 'auto' -> {mode: 'AUTO'}
        - 'none' -> {mode: 'NONE'}
        - 'required' -> {mode: 'ANY'}
        - {tool: 'name'} -> {mode: 'ANY', allowed_function_names: ['name']}

        Args:
            choice: Moxn tool_choice value

        Returns:
            Google function_calling_config value
        """
        if isinstance(choice, str):
            if choice == "auto":
                return {"mode": "AUTO"}
            elif choice == "none":
                return {"mode": "NONE"}
            elif choice == "required":
                return {"mode": "ANY"}
            else:
                # Unknown string, try to use as mode
                return {"mode": choice.upper()}

        if isinstance(choice, dict) and "tool" in choice:
            # {tool: 'name'} -> {mode: 'ANY', allowed_function_names: ['name']}
            return {
                "mode": "ANY",
                "allowed_function_names": [choice["tool"]],
            }

        # Pass through any other dict format unchanged
        return choice
