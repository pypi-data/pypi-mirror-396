from abc import ABC, abstractmethod
from typing import Any, Optional

import PIL.Image

from ..types import TaskResponse, TaskStatus


class Engine(ABC):
    """Abstract interface for Dojo engines"""

    @abstractmethod
    async def create_task(
        self,
        task_id: str,
        state: dict[str, Any],
        metadata: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Create a task execution"""
        pass

    @abstractmethod
    async def start_task(self, exec_id: str):
        """Start a task execution"""
        pass

    @abstractmethod
    async def get_task_status(self, exec_id: str) -> TaskResponse:
        """Get task status at a specific step"""
        pass

    @abstractmethod
    async def submit_action(
        self,
        exec_id: str,
        action: dict[str, Any],
        agent_response: str = "No thoughts provided",
        raw_response: str = "Not provided",
    ) -> dict[str, Any]:
        """Submit an action for a task"""
        pass

    @abstractmethod
    async def submit_step_score(self, exec_id: str, step_number: int, score: float) -> dict[str, Any]:
        """Submit a step score for a task"""
        pass

    @abstractmethod
    async def get_image(self, path: str) -> PIL.Image.Image:
        """Get an image from the server"""
        pass

    @abstractmethod
    async def stop_task(self, exec_id: str, status: TaskStatus = TaskStatus.COMPLETED) -> dict[str, Any]:
        """Stop a task execution"""
        pass

    @abstractmethod
    def stop_task_sync(self, exec_id: str, status: TaskStatus = TaskStatus.COMPLETED) -> dict[str, Any]:
        """Stop a task execution synchronously"""
        pass

    @abstractmethod
    async def query_storage(self, exec_id: str, query: dict[str, Any]) -> dict[str, Any]:
        """Query the storage server for a task execution"""
        pass
