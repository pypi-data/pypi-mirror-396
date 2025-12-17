from typing import Sequence

from moxn.models.prompt import PromptTemplate
from moxn.types.base import BaseTask


class Task(BaseTask[PromptTemplate]):
    """SDK Task model with business logic."""

    prompts: Sequence[PromptTemplate]
    # definitions inherited from BaseTask

    def get_prompt_by_name(self, name: str) -> PromptTemplate:
        """Get a prompt by its name"""
        matching = [r for r in self.prompts if r.name == name]
        if not matching:
            raise ValueError(f"No prompt found with name: {name}")
        if len(matching) > 1:
            raise ValueError(f"Multiple prompts found with name: {name}")
        return matching[0]

    def get_prompt_by_id(self, prompt_id: str) -> PromptTemplate:
        """Get a prompt by its ID"""
        matching = [r for r in self.prompts if r.id == prompt_id]
        if not matching:
            raise ValueError(f"No prompt found with ID: {prompt_id}")
        if len(matching) > 1:
            raise ValueError(f"Multiple prompts found with ID: {prompt_id}")
        return matching[0]
