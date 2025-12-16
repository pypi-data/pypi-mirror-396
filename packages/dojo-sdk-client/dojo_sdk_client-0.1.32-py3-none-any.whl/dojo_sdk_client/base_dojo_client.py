import logging
from io import BytesIO
from typing import Any, Optional

import aiohttp
import PIL.Image
import requests
from dojo_sdk_core.settings import settings
from dojo_sdk_core.ws_types import HistoryStep

from .telemetry.dojo_telemetry import telemetry
from .types import NoRunnersAvailableError, TaskResponse, TaskStatus

logger = logging.getLogger(__name__)


async def _handle_error_response_async(
    response: aiohttp.ClientResponse, context: dict[str, Any], request_body: Any = None
) -> None:
    """Log detailed error information before raising for async requests"""
    if response.status >= 400:
        try:
            error_body = await response.text()
            context_str = "\n".join(f"  {key}: {value}" for key, value in context.items())
            logger.error(
                f"HTTP {response.status} error:\n"
                f"  URL: {response.url}\n"
                f"  Request body: {request_body}\n"
                f"  Status: {response.status} {response.reason}\n"
                f"{context_str}\n"
                f"  Response body: {error_body}"
            )
        except Exception as e:
            logger.error(f"Failed to read error response body: {e}")
        response.raise_for_status()


def _handle_error_response_sync(response: requests.Response, context: dict[str, Any], request_body: Any = None) -> None:
    """Log detailed error information before raising for sync requests"""
    if response.status_code >= 400:
        try:
            error_body = response.text
            context_str = "\n".join(f"  {key}: {value}" for key, value in context.items())
            logger.error(
                f"HTTP {response.status_code} error:\n"
                f"  URL: {response.url}\n"
                f"  Request body: {request_body}\n"
                f"  Status: {response.status_code} {response.reason}\n"
                f"{context_str}\n"
                f"  Response body: {error_body}"
            )
        except Exception as e:
            logger.error(f"Failed to read error response body: {e}")
        response.raise_for_status()


class BaseDojoClient:
    """Barebones HTTP client for Dojo"""

    def __init__(self, api_key: str) -> None:
        if not api_key or api_key == "":
            raise ValueError(
                "API key is required.\n\n"
                "To get started:\n"
                "  1. Sign up at https://trydojo.ai/\n"
                "  2. Get your API key from settings\n"
                "  3. Pass it to the client: DOJO_API_KEY=your-api-key"
            )
        self.api_key: str = api_key
        self.http_endpoint: str = settings.dojo_http_endpoint
        self.tasks = set()

    def _get_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    @telemetry.track("create_task")
    async def create_task(
        self,
        task_id: str,
        state: dict[str, Any],
        metadata: Optional[dict[str, str]] = None,
        engine: str = "docker",
    ) -> dict[str, Any]:
        """Create a task execution"""
        async with aiohttp.request(
            "POST",
            f"{self.http_endpoint}/tasks",
            json={
                "task_id": task_id,
                "metadata": metadata if metadata is not None else None,
                "state": state,
                "engine": engine,
            },
            headers=self._get_headers(),
        ) as response:
            await _handle_error_response_async(
                response,
                {"Operation": "create_task", "Task ID": task_id},
                {"task_id": task_id, "metadata": metadata, "state": state, "engine": engine},
            )
            resp = await response.json()
            exec_id = resp["exec_id"]
            return exec_id

    @telemetry.track_sync("create_task_sync")
    def create_task_sync(
        self,
        task_id: str,
        state: dict[str, Any],
        metadata: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Create a task execution"""
        response = requests.post(
            f"{self.http_endpoint}/tasks",
            json={
                "task_id": task_id,
                "metadata": metadata or {},
                "state": state,
            },
            headers=self._get_headers(),
        )
        _handle_error_response_sync(response, {"Operation": "create_task_sync", "Task ID": task_id})
        resp = response.json()
        return resp["exec_id"]

    @telemetry.track("start_task")
    async def start_task(self, exec_id: str):
        """Start a task execution"""
        async with aiohttp.request(
            "POST",
            f"{self.http_endpoint}/tasks/start",
            json={"exec_id": exec_id},
            headers=self._get_headers(),
        ) as response:
            if response.status == 200:
                return

            resp = await response.json()
            if resp.get("error") == "TASK_CAPACITY_REACHED":
                raise NoRunnersAvailableError()
            else:
                await _handle_error_response_async(
                    response, {"Operation": "start_task", "Exec ID": exec_id}, {"exec_id": exec_id}
                )

    @telemetry.track_sync("start_task_sync")
    def start_task_sync(self, exec_id: str):
        """Start a task execution"""
        response = requests.post(
            f"{self.http_endpoint}/tasks/start",
            json={"exec_id": exec_id},
            headers=self._get_headers(),
        )
        _handle_error_response_sync(response, {"Operation": "start_task_sync", "Exec ID": exec_id})
        return

    @telemetry.track("track_start")
    async def track_start(self, exec_id: str, screenshot_base64: Optional[str] = None, state: Optional[dict[str, Any]] = None):
        """Track initial state and screenshot for engines that need it"""
        async with aiohttp.request(
            "POST",
            f"{self.http_endpoint}/tasks/start/track",
            json={
                "exec_id": exec_id,
                "screenshot": screenshot_base64,
                "state": state,
            },
            headers=self._get_headers(),
        ) as response:
            await _handle_error_response_async(response, {"Operation": "track_start", "Exec ID": exec_id})
            return await response.json()

    @telemetry.track("get_task_status")
    async def get_task_status(self, exec_id: str) -> TaskResponse:
        """Get task status at a specific step"""
        async with aiohttp.request(
            "GET", f"{self.http_endpoint}/tasks/{exec_id}/status", headers=self._get_headers()
        ) as response:
            await _handle_error_response_async(response, {"Operation": "get_task_status", "Exec ID": exec_id})
            result = await response.json()
            history = result.get("history", [])
            if history is None:
                history = []
            return TaskResponse(
                status=TaskStatus(result.get("status")),
                screenshot=result.get("screenshot"),
                history=[HistoryStep(**h) for h in history],
                step=result.get("step"),
                state=result.get("state"),
                failure_reason=result.get("failure_reason"),
            )

    @telemetry.track_sync("get_task_status_sync")
    def get_task_status_sync(self, exec_id: str) -> TaskResponse:
        """Get task status at a specific step"""
        response = requests.get(f"{self.http_endpoint}/tasks/{exec_id}/status", headers=self._get_headers())
        _handle_error_response_sync(response, {"Operation": "get_task_status_sync", "Exec ID": exec_id})
        result = response.json()
        history = result.get("history", [])
        if history is None:
            history = []
        return TaskResponse(
            status=TaskStatus(result.get("status")),
            screenshot=result.get("screenshot"),
            history=[HistoryStep(**h) for h in history],
            step=result.get("step"),
            state=result.get("state"),
            failure_reason=result.get("failure_reason"),
        )

    @telemetry.track("submit_action")
    async def submit_action(
        self,
        exec_id: str,
        action: dict[str, Any],
        agent_response: str = "No thoughts provided",
        raw_response: str = "Not provided",
    ) -> dict[str, Any]:
        """Submit an action for a task"""
        async with aiohttp.request(
            "POST",
            f"{self.http_endpoint}/tasks/actions",
            json={
                "action": action,
                "agent_response": agent_response,
                "exec_id": exec_id,
                "raw_response": raw_response,
            },
            headers=self._get_headers(),
        ) as response:
            await _handle_error_response_async(
                response,
                {"Operation": "submit_action", "Exec ID": exec_id},
                {"action": action, "agent_response": agent_response, "exec_id": exec_id, "raw_response": raw_response},
            )
            return await response.json()

    @telemetry.track_sync("submit_action_sync")
    def submit_action_sync(
        self,
        exec_id: str,
        action: dict[str, Any],
        agent_response: str = "No thoughts provided",
        raw_response: str = "Not provided",
    ) -> dict[str, Any]:
        """Submit an action for a task"""
        response = requests.post(
            f"{self.http_endpoint}/tasks/actions",
            json={
                "action": action,
                "agent_response": agent_response,
                "exec_id": exec_id,
                "raw_response": raw_response,
            },
            headers=self._get_headers(),
        )
        _handle_error_response_sync(response, {"Operation": "submit_action_sync", "Exec ID": exec_id})
        return response.json()

    @telemetry.track("track_action")
    async def track_action(
        self,
        exec_id: str,
        step_number: int,
        before_screenshot_base64: Optional[str] = None,
        after_screenshot_base64: Optional[str] = None,
        state: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Track action execution with screenshots and state for engines that need it"""
        async with aiohttp.request(
            "POST",
            f"{self.http_endpoint}/tasks/actions/track",
            json={
                "exec_id": exec_id,
                "step_number": step_number,
                "before_screenshot": before_screenshot_base64,
                "after_screenshot": after_screenshot_base64,
                "state": state,
            },
            headers=self._get_headers(),
        ) as response:
            await _handle_error_response_async(response, {"Operation": "track_action", "Exec ID": exec_id, "Step": step_number})
            return await response.json()

    @telemetry.track("submit_step_score")
    async def submit_step_score(self, exec_id: str, step_number: int, score: float) -> dict[str, Any]:
        """Submit a step score for a task"""
        async with aiohttp.request(
            "POST",
            f"{self.http_endpoint}/tasks/{exec_id}/submit_step_score",
            json={"step_number": step_number, "score": score},
            headers=self._get_headers(),
        ) as response:
            await _handle_error_response_async(
                response, {"Operation": "submit_step_score", "Exec ID": exec_id, "Step": step_number, "Score": score}
            )
            return await response.json()

    @telemetry.track_sync("submit_step_score_sync")
    def submit_step_score_sync(self, exec_id: str, step_number: int, score: float) -> dict[str, Any]:
        """Submit a step score for a task"""
        response = requests.post(
            f"{self.http_endpoint}/tasks/{exec_id}/submit_step_score",
            json={"step_number": step_number, "score": score},
            headers=self._get_headers(),
        )
        _handle_error_response_sync(
            response, {"Operation": "submit_step_score_sync", "Exec ID": exec_id, "Step": step_number, "Score": score}
        )
        return response.json()

    @telemetry.track("get_image")
    async def get_image(self, path: str) -> PIL.Image.Image:
        """Get an image from the server"""
        async with aiohttp.request("GET", f"{self.http_endpoint}/image?path={path}", headers=self._get_headers()) as response:
            await _handle_error_response_async(response, {"Operation": "get_image", "Path": path})
            return PIL.Image.open(BytesIO(await response.read()))

    @telemetry.track_sync("get_image_sync")
    def get_image_sync(self, path: str) -> PIL.Image.Image:
        """Get an image from the server"""
        response = requests.get(f"{self.http_endpoint}/image?path={path}", headers=self._get_headers())
        _handle_error_response_sync(response, {"Operation": "get_image_sync", "Path": path})
        return PIL.Image.open(BytesIO(response.content))

    @telemetry.track("stop_task")
    async def stop_task(self, exec_id: str, status: TaskStatus = TaskStatus.COMPLETED) -> dict[str, Any]:
        """Stop a task execution"""
        async with aiohttp.request(
            "POST", f"{self.http_endpoint}/tasks/stop", json={"exec_id": exec_id, "status": status}, headers=self._get_headers()
        ) as response:
            await _handle_error_response_async(response, {"Operation": "stop_task", "Exec ID": exec_id})
            return await response.json()

    @telemetry.track_sync("stop_task_sync")
    def stop_task_sync(self, exec_id: str, status: TaskStatus = TaskStatus.COMPLETED) -> dict[str, Any]:
        """Stop a task execution synchronously"""
        response = requests.post(
            f"{self.http_endpoint}/tasks/stop",
            json={"exec_id": exec_id, "status": status},
            headers=self._get_headers(),
            timeout=5,
        )
        _handle_error_response_sync(response, {"Operation": "stop_task_sync", "Exec ID": exec_id})
        return response.json()

    @telemetry.track("query_storage")
    async def query_storage(self, exec_id: str, query: dict[str, Any]) -> dict[str, Any]:
        """Query the storage server for a task execution"""
        async with aiohttp.request(
            "GET",
            f"{self.http_endpoint}/tasks/{exec_id}/query",
            json=query,
            headers=self._get_headers(),
        ) as response:
            await _handle_error_response_async(
                response,
                {"Operation": "query_storage", "Exec ID": exec_id},
                query,
            )
            return await response.json()

    @telemetry.track_sync("query_storage_sync")
    def query_storage_sync(self, exec_id: str, query: dict[str, Any]) -> dict[str, Any]:
        """Query the storage server for a task execution synchronously"""
        response = requests.get(
            f"{self.http_endpoint}/tasks/{exec_id}/query",
            json=query,
            headers=self._get_headers(),
        )
        _handle_error_response_sync(response, {"Operation": "query_storage_sync", "Exec ID": exec_id}, query)
        return response.json()
