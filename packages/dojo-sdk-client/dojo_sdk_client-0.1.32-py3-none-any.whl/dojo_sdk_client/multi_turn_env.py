import asyncio
import atexit
import base64
import json
import logging
import os
import time
import traceback
from io import BytesIO
from typing import Any, Callable, List, Tuple

import verifiers as vf
from datasets import Dataset
from dojo_sdk_core import WaitAction
from dojo_sdk_core.settings import settings
from dojo_sdk_core.tasks import RemoteTaskLoader, RewardNotFoundError
from dojo_sdk_core.types import (
    Action,
    ClickAction,
    DoneAction,
)
from verifiers.types import Message, Messages, State

from .agents.anthropic_cua import SYSTEM_PROMPT
from .agents.computer_use_tool import computer_tool
from .base_dojo_client import NoRunnersAvailableError, TaskStatus
from .engines import Engine, select_engine
from .utils import load_tasks_from_hf_dataset

logger = logging.getLogger(__name__)


def load_benchmark_tasks(tasks: List[str], task_loader: RemoteTaskLoader, system_prompt: str) -> Dataset:
    dataset_rows = []
    for task_id in tasks:
        try:
            task = task_loader.load_task(task_id)
        except RewardNotFoundError:
            logger.error(f"reward for {task_id} not found. Skipping task")
            continue
        dataset_rows.append(
            {
                "prompt": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task.instructions.user_prompt},
                ],
                "answer": "",
                "task": task.name,
                "info": {
                    "task_id": task_id,
                    "task_name": task.name,
                    "initial_state": json.dumps(task.initial_state),
                    "max_steps": task.max_steps,
                },
            }
        )

    return Dataset.from_list(dataset_rows)


class DojoReward:
    def __init__(self, engine: Engine, task_loader: RemoteTaskLoader, verbose: bool = False):
        self.client = engine
        self.verbose = verbose
        self.task_loader = task_loader

    @property
    def __name__(self) -> str:
        return "DojoReward"

    def _calculate_reward(self, task_id: str, initial_state_json: str, final_state: dict) -> Tuple[float, str]:
        """Calculate reward for a given task state."""
        task_def = self.task_loader.load_task(task_id)
        validate_frontend = task_def.reward["validate_frontend"]
        initial_state = json.loads(initial_state_json)
        return validate_frontend(initial_state, final_state)

    async def __call__(self, **kwargs: Any) -> float:
        try:
            state = kwargs.get("state", None)
            if state is None:
                logger.error("No state found in reward function")
                return 0.0

            exec_id = state.get("exec_id", None)
            if not exec_id:
                logger.error("No exec_id found in state")
                return 0.0

            task_id = state.get("task_id", None)
            if not task_id:
                logger.error("No task_id found in state")
                return 0.0

            # Get the final task state from the server
            task_response = await self.client.get_task_status(exec_id)

            if task_response.state is None:
                return 0.0

            # Calculate reward using the extracted helper method
            final_score, reason = self._calculate_reward(task_id, state.get("initial_state", "{}"), task_response.state)

            if self.verbose:
                logger.info(f"Task {exec_id} ({task_id}) reward: {final_score:.2f} - {reason}")

            return final_score
        except Exception as e:
            logger.error(f"Error calculating reward: {e} {traceback.format_exc()}")
            return 0.0


class DojoMultiTurnEnv(vf.ToolEnv):
    def __init__(
        self,
        engine: Engine,
        dataset: Dataset,
        task_loader: RemoteTaskLoader,
        **kwargs,
    ):
        self.engine = engine
        self.task_loader = task_loader
        self._created_time = time.time()
        self.verbose = kwargs.get("verbose", False)
        # Track all active exec_ids
        self.active_exec_ids = set()
        self._cleanup_done = False
        super().__init__(dataset=dataset, **kwargs, tools=[computer_tool])
        atexit.register(self.cleanup)

    def _log_verbose(self, message: str):
        """Helper to log messages only when verbose is enabled."""
        if self.verbose:
            logger.info(message)

    def _stop_and_cleanup(self, exec_id: str, status: TaskStatus = TaskStatus.COMPLETED):
        """Stop task and cleanup exec_id atomically."""
        # Synchronous version
        try:
            self.engine.stop_task_sync(exec_id, status)
        except Exception as e:
            logger.error(f"Error stopping task {exec_id}: {e}")
        self.active_exec_ids.discard(exec_id)

    async def _stop_and_cleanup_async(self, exec_id: str, status: TaskStatus = TaskStatus.COMPLETED):
        """Stop task and cleanup exec_id atomically (async version)."""
        try:
            await self.engine.stop_task(exec_id, status=status)
        except Exception as e:
            logger.error(f"Error stopping task {exec_id}: {e} {traceback.format_exc()}")
        self.active_exec_ids.discard(exec_id)

    def _calculate_step_reward(self, state: State, task_state: dict) -> Tuple[float, str]:
        """Calculate reward for a step using the task's reward function."""
        try:
            task_id = state.get("task_id")
            task_def = self.task_loader.load_task(task_id)
            reward_function = task_def.load_reward_function()
            initial_state = json.loads(state.get("initial_state", "{}"))
            return reward_function(initial_state, task_state)
        except Exception as e:
            logger.error(f"Error calculating step reward for {task_id}: {e} {traceback.format_exc()}")
            return 0.0, "Error calculating step reward"

    def _create_error_response(self, message: str) -> List[Message]:
        """Create a standard error response message."""
        return [{"role": "user", "content": message}]

    async def setup_state(self, state: State, **kwargs) -> State:
        info = state.get("info")

        state["task_id"] = info.get("task_id")
        state["initial_state"] = info.get("initial_state")
        state["max_steps"] = min(self.max_turns, info.get("max_steps"))
        state["step"] = 1
        state["started"] = False
        state["created"] = False

        return state

    async def _parse_tool_calls(self, messages: Messages) -> Tuple[List[Action], List[Message]]:
        actions = []
        tool_messages = []
        if "tool_calls" in messages[-1]:
            for tool_call in messages[-1]["tool_calls"]:
                tool_name: str = tool_call.get("function", {}).get("name", "")
                tool_call_id: str = tool_call.get("id", "")

                # Safely parse tool arguments with error handling
                arguments_str = tool_call.get("function", {}).get("arguments", "")
                try:
                    # Handle empty string case
                    if not arguments_str or arguments_str.strip() == "":
                        tool_args = {}
                    else:
                        tool_args = json.loads(arguments_str)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse tool arguments for {tool_name}: {e}")
                    logger.error(f"Malformed JSON: {arguments_str}")
                    tool_args = {}

                tool_message: Message = await self.call_tool(tool_name, tool_args, tool_call_id)
                tool_messages.append(tool_message)
                try:
                    action = computer_tool(**tool_args)
                    actions.append(action)
                except Exception as e:
                    logger.error(f"Error in computer_tool: {e} falling back to click")
                    action = ClickAction(x=100, y=100)
        return actions, tool_messages

    async def _create_task(self, state: State) -> str:
        exec_id = await self.engine.create_task(state["task_id"], json.loads(state["initial_state"]), metadata={})
        state["exec_id"] = exec_id
        state["created"] = True
        # Track this exec_id
        self.active_exec_ids.add(exec_id)
        self._log_verbose(f"Created task {state['task_id']}")
        return exec_id

    async def env_response(self, messages: Messages, state: State, **kwargs: Any) -> Tuple[Messages, State]:
        if state.get("failed", False):
            return self._create_error_response("Task failed"), state

        if not state.get("created", False):
            try:
                exec_id = await self._create_task(state)
            except Exception as e:
                state["failed"] = True
                logger.error(f"Error creating task: {e}")
                return self._create_error_response("Error creating task"), state

        exec_id = state.get("exec_id")
        if not exec_id:
            raise ValueError("Execution ID not found in state")

        while not state.get("started", False):
            # Start the task using DojoClient
            try:
                await self.engine.start_task(exec_id=state.get("exec_id"))
            except NoRunnersAvailableError:
                self._log_verbose("No runners available, retrying in 2 seconds")
                await asyncio.sleep(2)
                continue
            except Exception as e:
                logger.error(f"Error starting task {state['exec_id']}: {e}")
                state["failed"] = True
                return self._create_error_response("Error starting task"), state

            self._log_verbose(f"Started task {state['exec_id']}")
            state["started"] = True

            result, error = await self._try_or_abort(exec_id, self.engine.get_task_status, exec_id)
            if error:
                state["failed"] = True
                return self._create_error_response("Error getting task status"), state

            while result.status is TaskStatus.QUEUED:
                self._log_verbose(f"Task {exec_id} is queued, retrying in 1 second")
                await asyncio.sleep(1)
                result, error = await self._try_or_abort(exec_id, self.engine.get_task_status, exec_id)
                if error:
                    state["failed"] = True
                    return self._create_error_response("Error getting task status"), state

        # Get the last assistant message (most recent agent response)
        last_assistant_message = None
        for message in reversed(messages):
            if isinstance(message, dict) and message.get("role") == "assistant":
                last_assistant_message = message
                break

        if not last_assistant_message:
            logger.error("No assistant message found in messages")
            return self._create_error_response("No assistant message found in messages"), state

        # Extract content for logging
        last_message_content = last_assistant_message.get("content", "")

        actions, tool_messages = await self._parse_tool_calls(messages)
        self._log_verbose(f"Last message: {last_message_content} actions: {actions}")

        response_messages = []

        # TODO: Detect when the agent is done and submit the done messages
        if len(actions) == 0:
            response_messages.append(
                {"role": "user", "content": "No actions provided. To mark the task as complete, use the done action."}
            )
            actions.append(WaitAction(seconds=1))

        if isinstance(actions[0], DoneAction):
            await self._stop_and_cleanup_async(exec_id, TaskStatus.COMPLETED)
            return tool_messages + self._create_error_response("Agent has marked the task as complete"), state

        self._log_verbose(f"Step: {state.get('step', 0)} Max steps: {state.get('max_steps', self.max_turns)}")

        # Submit action using DojoClient with the complete assistant message
        task_response, error = await self._try_or_abort(
            exec_id,
            self.engine.submit_action,
            exec_id,
            actions[0].model_dump(),
            last_message_content if isinstance(last_message_content, str) else str(last_message_content),
            json.dumps(last_assistant_message),
        )
        if error:
            state["failed"] = True
            return tool_messages + self._create_error_response("Error submitting action for task"), state

        task_response, error = await self._try_or_abort(exec_id, self.engine.get_task_status, exec_id)
        if error:
            state["failed"] = True
            return tool_messages + self._create_error_response("Error getting task status"), state

        step_score, reason = self._calculate_step_reward(state, task_response.state)
        _, error = await self._try_or_abort(exec_id, self.engine.submit_step_score, exec_id, task_response.step - 1, step_score)
        if error:
            state["failed"] = True
            return tool_messages + self._create_error_response("Error submitting step score"), state
        self._log_verbose(f"Step {task_response.step} score: {step_score:.2f} - {reason}")

        screenshot_path = task_response.screenshot
        history = task_response.history

        state["step"] = task_response.step
        state["history"] = history

        # Get the image from the server
        image, error = await self._try_or_abort(exec_id, self.engine.get_image, screenshot_path)
        if error:
            state["failed"] = True
            return tool_messages + self._create_error_response("Error getting image"), state

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        screenshot_bytes = buffer.getvalue()
        b64_img = base64.b64encode(screenshot_bytes).decode("utf-8")

        response_messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64_img}"},
                    }
                ],
            }
        )

        self._log_verbose(f"Environment responded for task {exec_id} with step {state['step']}")

        return tool_messages + response_messages, state

    async def is_completed(self, messages: Messages, state: State, **kwargs: Any) -> bool:
        """Check if the task is completed."""
        failed = state.get("failed", False)
        if failed:
            return True

        created = state.get("created", False)
        started = state.get("started", False)
        if not created or not started:
            return False

        exec_id = state.get("exec_id", None)
        if not exec_id:
            raise ValueError("Execution ID not found in state")

        if state.get("step", 0) >= state.get("max_steps", self.max_turns):
            await self._stop_and_cleanup_async(exec_id, TaskStatus.COMPLETED)
            return True

        # Check task status
        task_response, error = await self._try_or_abort(exec_id, self.engine.get_task_status, exec_id)
        if error:
            state["failed"] = True
            return True

        is_finished = task_response.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELED)

        if is_finished:
            await self._stop_and_cleanup_async(exec_id, TaskStatus.COMPLETED)
        return is_finished

    async def _try_or_abort(self, exec_id: str, func: Callable, *args: Any, **kwargs: Any) -> Tuple[Any, bool]:
        try:
            result = await func(*args, **kwargs)
            return result, False
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e} {traceback.format_exc()}")
            await self._stop_and_cleanup_async(exec_id, TaskStatus.CANCELED)
            return None, True

    def cleanup(self):
        """Cleanup method called on exit. Stops all active tasks."""
        if self._cleanup_done:
            return
        self._cleanup_done = True

        if self.active_exec_ids:
            logger.info(f"Cleaning up {len(self.active_exec_ids)} active tasks")
            for exec_id in list(self.active_exec_ids):  # Create copy to avoid modification during iteration
                self._log_verbose(f"Stopping task {exec_id}")
                self._stop_and_cleanup(exec_id, TaskStatus.CANCELED)
            self.active_exec_ids.clear()


def load_environment(API_KEY: str, system_prompt: str, tasks: List[str], **kwargs):
    """Load the Dojo environment. The environment must be executed within a minute or it will be terminated."""

    # Load execution engine
    engine = select_engine(API_KEY)

    # Create all tasks
    task_loader = RemoteTaskLoader("chakra-labs/dojo-bench-customer-colossus")
    tasks_dataset = load_benchmark_tasks(tasks, task_loader, system_prompt)

    rubric = vf.Rubric(
        funcs=[DojoReward(engine, task_loader)],
        weights=[1.0],
    )

    env = DojoMultiTurnEnv(
        engine=engine,
        dataset=tasks_dataset,
        task_loader=task_loader,
        max_turns=kwargs.get("max_turns", 50),
        rubric=rubric,
        **kwargs,
    )

    return env


async def main():
    from openai import AsyncOpenAI

    tasks = load_tasks_from_hf_dataset("chakra-labs/dojo-bench-customer-colossus")

    API_KEY = os.getenv("DOJO_API_KEY")
    env = load_environment(
        API_KEY=API_KEY,
        system_prompt=SYSTEM_PROMPT
        + (
            "\n\nScreenshots are always provided as input. DO NOT ASK FOR A SCREENSHOT OR TRY TO TAKE A SCREENSHOT. "
            "DO NOT ASK FOR ANY INSTRUCTION FROM THE USER. When you are done, you must use the done action. "
            "Always perform an action"
        ),
        tasks=tasks,
    )

    client = AsyncOpenAI(api_key=settings.anthropic_api_key, base_url="https://api.anthropic.com/v1/")
    eval_result = await env.evaluate(
        client=client,
        model="claude-4-sonnet-20250514",
    )
    print(f"Task: {eval_result.task}")
    print(f"Metrics: {eval_result.metrics}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
