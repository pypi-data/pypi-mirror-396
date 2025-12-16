from typing import Any, Optional

import PIL.Image

from ..base_dojo_client import BaseDojoClient
from ..types import TaskResponse, TaskStatus
from .engine import Engine


class DojoEngine(Engine):
    """Dojo engine implementation"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = BaseDojoClient(api_key)

    async def create_task(
        self,
        task_id: str,
        state: dict[str, Any],
        metadata: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Create a task execution"""
        return await self.client.create_task(task_id, state, metadata, "docker")

    async def start_task(self, exec_id: str):
        """Start a task execution"""
        return await self.client.start_task(exec_id)

    async def get_task_status(self, exec_id: str) -> TaskResponse:
        """Get task status at a specific step"""
        return await self.client.get_task_status(exec_id)

    async def submit_action(
        self,
        exec_id: str,
        action: dict[str, Any],
        agent_response: str = "No thoughts provided",
        raw_response: str = "Not provided",
    ) -> dict[str, Any]:
        """Submit an action for a task"""
        return await self.client.submit_action(exec_id, action, agent_response, raw_response)

    async def submit_step_score(self, exec_id: str, step_number: int, score: float) -> dict[str, Any]:
        """Submit a step score for a task"""
        return await self.client.submit_step_score(exec_id, step_number, score)

    async def get_image(self, path: str) -> PIL.Image.Image:
        """Get an image from the server"""
        return await self.client.get_image(path)

    async def stop_task(self, exec_id: str, status: TaskStatus = TaskStatus.COMPLETED) -> dict[str, Any]:
        """Stop a task execution"""
        return await self.client.stop_task(exec_id, status=status)

    def stop_task_sync(self, exec_id: str, status: TaskStatus = TaskStatus.COMPLETED) -> dict[str, Any]:
        """Stop a task execution synchronously"""
        return self.client.stop_task_sync(exec_id, status=status)

    async def query_storage(self, exec_id: str, query: dict[str, Any]) -> dict[str, Any]:
        """Query the storage server for a task execution"""
        return await self.client.query_storage(exec_id, query)
