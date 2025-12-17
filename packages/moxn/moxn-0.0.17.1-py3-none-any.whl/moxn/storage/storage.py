from moxn.models.prompt import PromptTemplate
from moxn.models.task import Task
from moxn.storage.base import StorageBackend
from cachetools import TTLCache


class InMemoryStorage(StorageBackend):
    def __init__(self):
        # Immutable commit cache - never expires
        self._commit_cache: dict[tuple[str, str], Task | PromptTemplate] = {}
        # (commit_id, entity_id) -> entity

        # Branch resolution cache - 60 second TTL
        self._branch_cache: TTLCache = TTLCache(maxsize=1000, ttl=60)
        # (task_id, branch_name) -> commit_id

    async def store_task(self, task: Task, commit_id: str | None = None) -> None:
        """Store a task at a commit."""
        task_id = str(task.id)

        if commit_id:
            # Store in immutable commit cache
            cache_key = (commit_id, task_id)
            if cache_key not in self._commit_cache:
                self._commit_cache[cache_key] = task.model_copy(deep=True)

    async def store_prompt(
        self, prompt: PromptTemplate, commit_id: str | None = None
    ) -> None:
        """Store a prompt at a commit."""
        prompt_id = str(prompt.id)

        if commit_id:
            # Store in immutable commit cache
            cache_key = (commit_id, prompt_id)
            if cache_key not in self._commit_cache:
                self._commit_cache[cache_key] = prompt.model_copy(deep=True)

    async def get_task_by_commit(self, task_id: str, commit_id: str) -> Task:
        """Get task from immutable commit cache."""
        cache_key = (commit_id, task_id)
        if cache_key in self._commit_cache:
            entity = self._commit_cache[cache_key]
            if isinstance(entity, Task):
                return entity.model_copy(deep=True)
        raise KeyError(f"Task not found: {task_id} at commit: {commit_id}")

    async def get_task(self, task_id: str, commit_id: str) -> Task:
        """Get task from commit cache."""
        return await self.get_task_by_commit(task_id, commit_id)

    async def get_prompt_by_commit(
        self, prompt_id: str, commit_id: str
    ) -> PromptTemplate:
        """Get prompt from immutable commit cache."""
        cache_key = (commit_id, prompt_id)
        if cache_key in self._commit_cache:
            entity = self._commit_cache[cache_key]
            if isinstance(entity, PromptTemplate):
                return entity.model_copy(deep=True)
        raise KeyError(f"Prompt not found: {prompt_id} at commit: {commit_id}")

    async def get_prompt(self, prompt_id: str, commit_id: str) -> PromptTemplate:
        """Get prompt from commit cache."""
        return await self.get_prompt_by_commit(prompt_id, commit_id)

    async def has_task_commit(self, task_id: str, commit_id: str) -> bool:
        """Check if task exists at commit."""
        return (commit_id, task_id) in self._commit_cache

    async def has_prompt_commit(self, prompt_id: str, commit_id: str) -> bool:
        """Check if prompt exists at commit."""
        return (commit_id, prompt_id) in self._commit_cache

    async def cache_branch_resolution(
        self, task_id: str, branch_name: str, commit_id: str
    ) -> None:
        """Cache a branch to commit resolution."""
        cache_key = (task_id, branch_name)
        self._branch_cache[cache_key] = commit_id

    async def get_cached_branch_commit(
        self, task_id: str, branch_name: str
    ) -> str | None:
        """Get cached commit for a branch, if available."""
        cache_key = (task_id, branch_name)
        return self._branch_cache.get(cache_key)

    async def clear(self) -> None:
        """Clear all caches."""
        self._commit_cache.clear()
        self._branch_cache.clear()
