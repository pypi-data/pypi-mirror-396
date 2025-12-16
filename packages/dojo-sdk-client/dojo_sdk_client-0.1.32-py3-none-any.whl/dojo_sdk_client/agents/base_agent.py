from abc import ABC, abstractmethod

from dojo_sdk_core.types import Action


class BaseAgent(ABC):
    """Base agent class for all agents. A new agent will be created for each task."""

    @abstractmethod
    def get_next_action(self, *args, **kwargs) -> tuple[Action, str, str]:
        """Get the next action to take. Returns (action, reasoning, raw_response)."""
        raise NotImplementedError
