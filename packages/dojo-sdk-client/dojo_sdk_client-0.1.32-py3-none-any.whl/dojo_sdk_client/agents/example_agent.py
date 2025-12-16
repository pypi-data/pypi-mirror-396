import random
import time

from dojo_sdk_core.types import Action, ClickAction

from .base_agent import BaseAgent


class ExampleAgent(BaseAgent):
    """Simple local agent for demonstration purposes."""

    def __init__(self, model_path: str = "example"):
        self.model_path = model_path

    def _get_response(self, prompt: str, screenshot_path: str, history: list) -> str:
        # simulate a delay
        time.sleep(0.1)
        return f"click:{random.randint(300, 700)},{random.randint(300, 700)}"

    def get_next_action(self, prompt: str, screenshot_path: str, history: list) -> tuple[Action, str, str]:
        response = self._get_response(prompt, screenshot_path, history)

        if response.startswith("click:"):
            coords = response.split(":")[1]
            x, y = map(int, coords.split(","))
            return (
                ClickAction(x=x, y=y),
                "reasoning",
                "{}",
            )

        return (
            ClickAction(x=500, y=300),
            "reasoning",
            "{}",
        )
