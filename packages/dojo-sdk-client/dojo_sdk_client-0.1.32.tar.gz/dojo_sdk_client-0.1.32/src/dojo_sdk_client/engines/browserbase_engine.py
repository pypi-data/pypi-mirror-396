import asyncio
import base64
import logging

import PIL
from dojo_sdk_core import TaskDefinition
from dojo_sdk_core.models import Any
from dojo_sdk_core.settings import settings
from dojo_sdk_core.tasks import RemoteTaskLoader
from dojo_sdk_core.ws_types import Action, Optional

from ..base_dojo_client import BaseDojoClient
from ..telemetry.dojo_telemetry import telemetry
from ..types import NoRunnersAvailableError, TaskResponse, TaskStatus
from .browserController import BrowserController
from .engine import Engine

logger = logging.getLogger(__name__)


# TODO: Make it stateless meaning we don't need to track history, steps or connection info locally.
class BrowserBaseEngine(Engine):
    def __init__(self, api_key: str, project_id: str, dojo_api_key: str = None):
        self.api_key = api_key
        self.project_id = project_id
        self.concurrent_limit = settings.browserbase_concurrent_limit
        self.execid_to_taskdef = {}
        self.running_tasks = set()
        self.lock = asyncio.Lock()

        # TODO: Replace this with proper loading of definitions etc
        self.loader = RemoteTaskLoader(dataset_name="chakra-labs/dojo-bench-customer-colossus")

        self.browser_controller = BrowserController(api_key=api_key, project_id=project_id)
        self.sessions: dict[str, dict[str, Any]] = {}

        ## We use the dojo client for reporting scores and other coordination etc
        self.client = BaseDojoClient(dojo_api_key)

    @telemetry.track("create_task", engine="browserbase")
    async def create_task(
        self,
        task_id: str,
        state: dict[str, Any],
        metadata: Optional[dict[str, str]] = None,
    ) -> str:
        metadata = metadata or {}
        metadata["engine"] = "browserbase"
        task_def = self.loader.load_task(task_id)
        exec_id = await self.client.create_task(task_id, task_def.initial_state, engine="browserbase")
        self.execid_to_taskdef[exec_id] = task_def

        return exec_id

    @telemetry.track("start_task", engine="browserbase")
    async def start_task(self, exec_id: str):
        """Start a task execution - creates a browser session"""
        async with self.lock:
            if len(self.running_tasks) >= self.concurrent_limit:
                raise NoRunnersAvailableError()

            await self.client.start_task(exec_id)
            self.running_tasks.add(exec_id)

        session = await self.browser_controller.create_session()

        # Store session info (just the connection URL, no controller)
        self.sessions[exec_id] = {
            "session_id": session.id,
            "connect_url": session.connect_url,
        }

        connect_url = session.connect_url
        task_def: TaskDefinition = self.execid_to_taskdef[exec_id]

        await self.browser_controller.get(connect_url, task_def.environment.path, wait_until_loaded=True)
        await self.browser_controller.set_state(connect_url, task_def.initial_state)
        screenshot_bytes = await self.browser_controller.screenshot(connect_url)

        screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        track_result = await self.client.track_start(exec_id, screenshot_base64, state=task_def.initial_state)

        return track_result

    @telemetry.track("get_task_status", engine="browserbase")
    async def get_task_status(self, exec_id: str) -> TaskResponse:
        """Get task status - includes current browser state"""
        return await self.client.get_task_status(exec_id)

    @telemetry.track("submit_action", engine="browserbase")
    async def submit_action(
        self,
        exec_id: str,
        action: Action,
        agent_response: str = "No thoughts provided",
        raw_response: str = "Not provided",
    ) -> dict[str, Any]:
        """Submit an action for a task - executes the action in the browser"""
        if exec_id not in self.sessions:
            raise ValueError(f"No session found for exec_id: {exec_id}")

        connect_url = self.sessions[exec_id]["connect_url"]
        before_screenshot_bytes = await self.browser_controller.screenshot(connect_url)

        # Perform the action
        await self.browser_controller.perform_action(connect_url, action)

        # Get the new state and take a screenshot
        new_state = await self.browser_controller.get_state(connect_url)
        after_screenshot_bytes = await self.browser_controller.screenshot(connect_url)

        # Create history step (score will be updated later via submit_step_score)
        before_screenshot_base64 = base64.b64encode(before_screenshot_bytes).decode("utf-8")
        after_screenshot_base64 = base64.b64encode(after_screenshot_bytes).decode("utf-8")

        # Submit the action and get the step number from the server
        submit_result = await self.client.submit_action(exec_id, action, agent_response, raw_response)
        step_number = submit_result.get("next_step_number")

        logger.info(f"Current step: {step_number}")

        await self.client.track_action(
            exec_id,
            step_number=step_number,
            before_screenshot_base64=before_screenshot_base64,
            after_screenshot_base64=after_screenshot_base64,
            state=new_state,
        )

        return {"success": True, "state": new_state, "agent_response": agent_response}

    @telemetry.track("submit_step_score", engine="browserbase")
    async def submit_step_score(self, exec_id: str, step_number: int, score: float) -> dict[str, Any]:
        """Submit a step score for a task"""
        await self.client.submit_step_score(exec_id, step_number, score)

    @telemetry.track("get_image", engine="browserbase")
    async def get_image(self, path: str) -> PIL.Image.Image:
        """Get a screenshot from the browser"""
        return await self.client.get_image(path)

    @telemetry.track("stop_task", engine="browserbase")
    async def stop_task(self, exec_id: str, status: TaskStatus = TaskStatus.COMPLETED) -> dict[str, Any]:
        """Stop a task execution"""
        try:
            if exec_id not in self.sessions:
                return {"error": f"No session found for exec_id: {exec_id}"}

            session_info = self.sessions[exec_id]
            connect_url = session_info["connect_url"]
            await self.client.stop_task(exec_id, status=status)
            await self.browser_controller.terminate_session(connect_url)

            # Clean up tracking data
            del self.sessions[exec_id]

            return {"success": True}
        except Exception as e:
            logger.error(f"Error stopping task {exec_id}: {e}")
            return {"error": str(e)}
        finally:
            # Always remove from running_tasks, even if cleanup fails
            async with self.lock:
                self.running_tasks.discard(exec_id)

    @telemetry.track_sync("stop_task_sync", engine="browserbase")
    def stop_task_sync(self, exec_id: str, status: TaskStatus = TaskStatus.COMPLETED) -> dict[str, Any]:
        """Stop a task execution synchronously"""
        try:
            self.client.stop_task_sync(exec_id, status=status)
            try:
                if exec_id in self.sessions:
                    self.browser_controller.terminate_session_sync(self.sessions[exec_id]["connect_url"])
            except Exception as e:
                logger.error(f"Error terminating session {exec_id}: {e}")
                return {"error": str(e)}
            return
        except Exception as e:
            logger.error(f"Error stopping task {exec_id}: {e}")
            return {"error": str(e)}

    async def query_storage(self, exec_id: str, query: dict[str, Any]) -> dict[str, Any]:
        """Query the storage server for a task execution"""
        return await self.client.query_storage(exec_id, query)
