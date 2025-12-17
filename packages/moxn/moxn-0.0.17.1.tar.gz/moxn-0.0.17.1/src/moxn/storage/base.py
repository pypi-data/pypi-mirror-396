from abc import ABC, abstractmethod
from typing import TypeVar

from moxn.models.prompt import PromptTemplate
from moxn.models.task import Task

T = TypeVar("T", Task, PromptTemplate)


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    async def store_task(self, task: Task, commit_id: str | None = None) -> None:
        """Store a task at a commit."""
        pass

    @abstractmethod
    async def store_prompt(
        self, prompt: PromptTemplate, commit_id: str | None = None
    ) -> None:
        """Store a prompt at a commit."""
        pass

    @abstractmethod
    async def get_task(self, task_id: str, commit_id: str) -> Task:
        """Retrieve a task at a commit."""
        pass

    @abstractmethod
    async def get_prompt(self, prompt_id: str, commit_id: str) -> PromptTemplate:
        """Retrieve a prompt at a commit."""
        pass

    @abstractmethod
    async def has_task_commit(self, task_id: str, commit_id: str) -> bool:
        """Check if a task exists at commit."""
        pass

    @abstractmethod
    async def has_prompt_commit(self, prompt_id: str, commit_id: str) -> bool:
        """Check if a prompt exists at commit."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all stored data."""
        pass
