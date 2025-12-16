import base64
import io
import json
import logging
from typing import Any, Dict

from anthropic import Anthropic
from anthropic.types.beta import (
    BetaMessageParam,
    BetaTextBlockParam,
)
from dojo_sdk_core.settings import settings
from dojo_sdk_core.types import (
    Action,
    DoneAction,
    WaitAction,
)
from dojo_sdk_core.ws_types import HistoryStep
from PIL import Image

from .basic_cua import BasicCUA
from .computer_use_tool import computer_tool

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

API_RETRY_TIMES = 4
API_RETRY_INTERVAL = 2


SYSTEM_PROMPT = """
You are Claude, an AI assistant created by Anthropic. You can control the computer using a mouse and keyboard.

Key guidelines:
- You cannot ask for a screenshot, the user will always provide a screenshot as input
- Use precise coordinates for mouse actions
- Type text when needed for input fields
- Use keyboard shortcuts efficiently
- Complete tasks step by step
- If a task is complete or impossible, use the appropriate action
- Do not prompt the user for any information, just take actions
- You can reflect on your previous thoughts to see what actions you have taken and what you have not taken
- You are an autonomous agent, you do not need to ask the user for any action or confirmation
- YOU CANNOT TAKE A SCREENSHOT, THE USER WILL ALWAYS PROVIDE A SCREENSHOT AS INPUT

You have access to these tools:
- computer: For performing mouse actions
"""


class AnthropicCUA(BasicCUA):
    def __init__(
        self,
        model: str,
        image_context_length: int = 10,
        max_tokens: int = 4096,
        system_prompt_suffix: str = "",
        screen_size: tuple[int, int] = (1280, 800),
        verbose: bool = False,
    ):
        super().__init__(
            image_context_length=image_context_length,
            max_tokens=max_tokens,
            system_prompt_suffix=system_prompt_suffix,
            screen_size=screen_size,
            verbose=verbose,
        )
        self.model = model
        self.client = Anthropic(api_key=settings.anthropic_api_key)

        if self.verbose:
            logger.info(f"AnthropicCUA initialized with model: {model}, image_context_length: {image_context_length}")

    def history_to_messages(self, history: list[HistoryStep]) -> list[BetaMessageParam]:
        """Convert history to messages, reconstructing original message format from raw responses."""
        messages = []

        for i, step in enumerate(history):
            screenshot_base64 = self._get_cached_image(step.after_screenshot)

            # Check if previous step had a tool_use that needs a tool_result
            tool_use_id = None
            if i > 0:
                prev_step = history[i - 1]
                if prev_step.raw_response:
                    try:
                        prev_raw_data = json.loads(prev_step.raw_response)
                        if "content" in prev_raw_data:
                            for content_block in prev_raw_data["content"]:
                                if isinstance(content_block, dict) and content_block.get("type") == "tool_use":
                                    tool_use_id = content_block.get("id")
                                    break
                    except (json.JSONDecodeError, KeyError):
                        pass

            if tool_use_id:
                # This step is a tool_result for the previous tool_use
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": [
                                    {
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": "image/png",
                                            "data": screenshot_base64,
                                        },
                                    }
                                ],
                            }
                        ],
                    }
                )
            else:
                # Regular user message with screenshot
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": screenshot_base64,
                                },
                            }
                        ],
                    }
                )

            # Reconstruct assistant message from raw response
            if step.raw_response:
                try:
                    raw_data = json.loads(step.raw_response)

                    if "content" not in raw_data:
                        raise ValueError(f"No content found in raw_response for step {step.step}")

                    assistant_message = {
                        "role": raw_data["role"],
                        "content": raw_data["content"],
                    }

                    messages.append(assistant_message)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse raw_response for step {step.step}: {e}")
                    # Skip this step if we can't parse the raw response
                    continue

        return messages

    def get_next_action(self, prompt: str, image: Image.Image, history: list) -> tuple[Action, str, str]:
        """Get the next action to take based on the current state."""
        reasoning = None
        raw_response = ""
        try:
            obs = {"screenshot": image}
            trimmed_history = self._trim_history_to_context_window(history)
            messages = self.history_to_messages(trimmed_history)
            reasoning, actions, raw_response = self.predict(prompt, obs, messages=messages)

            if self.verbose:
                logger.info(
                    f"""

             PREDICT OUTPUT
             ================================

             REASONING: {reasoning}

             ACTIONS: {actions}

             """
                )

            if not actions or len(actions) == 0:
                raise ValueError("No actions provided")

            # Convert first action to Dojo Action format
            action_data = actions[0]
            if isinstance(action_data, str):
                if action_data == "DONE":
                    return DoneAction(), reasoning, raw_response
                if action_data == "WAIT":
                    return WaitAction(seconds=1), reasoning, raw_response
                else:
                    raise ValueError(f"Unknown action: {action_data}, only DONE is supported")

            if isinstance(action_data, dict):
                # Check if this is a wait action in dict format
                input_data = action_data.get("input", {})
                action_type = input_data.get("action", "")

                if action_type == "wait":
                    duration = input_data.get("duration", 1)
                    return WaitAction(seconds=duration), reasoning, raw_response

                try:
                    return (
                        self._convert_to_dojo_action(action_data),
                        reasoning,
                        raw_response,
                    )
                except ValueError as e:
                    if "Screenshot" in str(e):
                        return self.get_next_action(prompt, image, history)
                    # Handle unsupported actions gracefully - return wait and inform agent
                    unsupported_msg = f"Action '{action_type}' is not supported. Please use a different action."
                    logger.warning(f"Unsupported action received: {action_type}. Returning wait action.")
                    combined_reasoning = f"{reasoning}\n\n[SYSTEM: {unsupported_msg}]" if reasoning else unsupported_msg
                    return WaitAction(seconds=1), combined_reasoning, raw_response

        except Exception as e:
            raise ValueError(f"Error in get_next_action: {e}") from e

    def _convert_to_dojo_action(self, action_data: dict) -> Action:
        """Convert Claude's action format to Dojo Action format."""
        input_data = action_data.get("input", {})
        action = input_data.get("action", "")
        coordinate = input_data.get("coordinate")
        text = input_data.get("text")
        scroll_direction = input_data.get("scroll_direction")
        scroll_amount = input_data.get("scroll_amount")
        start_coordinate = input_data.get("start_coordinate")

        return computer_tool(action, coordinate, text, scroll_direction, scroll_amount, start_coordinate)

    def predict(
        self,
        task_instruction: str,
        obs: Dict = None,
        system: Any = None,
        messages: list[BetaMessageParam] = None,
    ):
        """Main prediction method adapted from your implementation."""
        system = BetaTextBlockParam(
            type="text",
            text=f"{SYSTEM_PROMPT}{' ' + self.system_prompt_suffix if self.system_prompt_suffix else ''}",
        )

        # Resize screenshot if needed
        if obs and "screenshot" in obs:
            screenshot_image = obs["screenshot"]

            # Resize to standard size
            new_width, new_height = self.screen_size
            resized_image = screenshot_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Convert back to bytes
            output_buffer = io.BytesIO()
            resized_image.save(output_buffer, format="PNG")
            obs["screenshot"] = output_buffer.getvalue()

        # Initialize messages as empty list if None
        if messages is None:
            messages = []

        # Initialize conversation if empty
        if len(messages) == 0:
            init_screenshot_base64 = base64.b64encode(obs["screenshot"]).decode("utf-8")
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": init_screenshot_base64,
                            },
                        },
                        {"type": "text", "text": task_instruction},
                    ],
                }
            )

        # Add tool result if previous message had tool use and no tool_result was already added
        if messages and messages[-1]["role"] == "assistant":
            last_content = messages[-1]["content"]
            if isinstance(last_content, list) and any(block.get("type") == "tool_use" for block in last_content):
                # Check if the next message is already a tool_result for this tool_use
                tool_use_block = next(block for block in last_content if block.get("type") == "tool_use")
                tool_use_id = tool_use_block["id"]

                # Only add tool_result if there isn't already one for this tool_use_id
                has_tool_result = False
                if len(messages) > 1:
                    # Check if there's already a tool_result message after this assistant message
                    # This would happen if we're in the middle of processing history
                    for msg in messages:
                        if msg["role"] == "user" and isinstance(msg["content"], list):
                            for content_block in msg["content"]:
                                if (
                                    content_block.get("type") == "tool_result"
                                    and content_block.get("tool_use_id") == tool_use_id
                                ):
                                    has_tool_result = True
                                    break
                            if has_tool_result:
                                break

                if not has_tool_result:
                    self._add_tool_result_to_messages(
                        messages,
                        tool_use_id,
                        "Success",
                        screenshot=obs.get("screenshot") if obs else None,
                    )

        # Prepare tools
        computer_tool = {
            "name": "computer",
            "type": "computer_20250124",  # default to the latest computer tool
            "display_width_px": self.screen_size[0],
            "display_height_px": self.screen_size[1],
            "display_number": 1,
        }
        beta = "computer-use-2025-01-24"
        if self.model == "claude-3-5-sonnet-20241022":
            computer_tool["type"] = "computer_20241022"
            beta = "computer-use-2024-10-22"

        try:
            response = self.client.beta.messages.create(
                max_tokens=self.max_tokens,
                messages=messages,
                model=self.model,
                system=[system],
                tools=[computer_tool],
                betas=[beta],
            )

            # Store raw response for history
            raw_response = response.model_dump_json()

            # Process response
            response_params = self._response_to_params(response)

            # Parse actions
            actions = []
            reasonings = []

            for content_block in response_params:
                if content_block["type"] == "tool_use":
                    actions.append(content_block)
                elif content_block["type"] == "text":
                    reasonings.append(content_block["text"])

            reasoning = reasonings[0] if reasonings else ""

            if len(actions) == 0:
                actions = ["DONE"]

            return reasoning, actions, raw_response

        except Exception as e:
            logger.error(f"Error in predict: {e}")
            raise ValueError(f"Error in predict: {e}") from e

    def _add_tool_result_to_messages(self, messages: list, tool_call_id: str, result: str, screenshot: bytes = None):
        """Add tool result to message list."""
        tool_result_content = [
            {
                "type": "tool_result",
                "tool_use_id": tool_call_id,
                "content": [{"type": "text", "text": result}],
            }
        ]

        # Add screenshot if provided
        if screenshot is not None:
            screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")
            tool_result_content[0]["content"].append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": screenshot_base64,
                    },
                }
            )

        messages.append({"role": "user", "content": tool_result_content})

    def _response_to_params(self, response):
        """Convert response to parameters format."""
        result = []
        for content_block in response.content:
            if content_block.type == "text":
                result.append({"type": "text", "text": content_block.text})
            elif content_block.type == "tool_use":
                result.append(
                    {
                        "type": "tool_use",
                        "id": content_block.id,
                        "name": content_block.name,
                        "input": content_block.input,
                    }
                )
        return result
