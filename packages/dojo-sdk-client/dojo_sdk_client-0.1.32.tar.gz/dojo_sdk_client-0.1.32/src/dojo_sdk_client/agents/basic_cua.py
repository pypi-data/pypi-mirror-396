import base64
import logging
from abc import abstractmethod

import requests
from dojo_sdk_core.settings import settings

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class BasicCUA(BaseAgent):
    """Base class for Computer Use Agents with common functionality."""

    def __init__(
        self,
        image_context_length: int = 10,
        max_tokens: int = 4096,
        system_prompt_suffix: str = "",
        screen_size: tuple[int, int] = (1280, 800),
        verbose: bool = False,
    ):
        self.image_context_length = image_context_length
        self.max_tokens = max_tokens
        self.system_prompt_suffix = system_prompt_suffix
        self.screen_size = screen_size
        self.verbose = verbose

        # Image cache to eliminate redundant downloads
        self._image_cache = {}  # path -> base64_string
        self._cache_size_mb = 0.0
        self._max_cache_size_mb = 100.0

    @abstractmethod
    def history_to_messages(self, history: list):
        """Convert history steps to model-specific message format."""
        raise NotImplementedError

    @abstractmethod
    def predict(self, task_instruction: str, obs: dict = None, messages: list = None):
        """Make a prediction using the model. Returns (reasoning, actions, raw_response)."""
        raise NotImplementedError

    def _trim_history_to_context_window(self, history: list) -> list:
        """Trim history to keep first step + last N steps within context window."""
        if len(history) <= self.image_context_length:
            return history
        return [history[0]] + history[-self.image_context_length :]

    def _get_cached_image(self, screenshot_path: str) -> str:
        """Get base64-encoded image from cache or download and cache it."""
        if screenshot_path in self._image_cache:
            return self._image_cache[screenshot_path]

        try:
            response = requests.get(f"{settings.dojo_http_endpoint}/image?path={screenshot_path}")
            screenshot_base64 = base64.b64encode(response.content).decode("utf-8")

            # Update cache
            self._image_cache[screenshot_path] = screenshot_base64
            self._cache_size_mb += len(screenshot_base64) / (1024 * 1024)

            # Prune if needed
            if self._cache_size_mb > self._max_cache_size_mb:
                self._prune_cache_to_context_window()

            return screenshot_base64

        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return ""

    def _prune_cache_to_context_window(self):
        """Remove old images from cache, keeping first + recent images."""
        if len(self._image_cache) <= self.image_context_length + 1:
            return

        # Cache keys are already in chronological order due to history trimming
        paths = list(self._image_cache.keys())

        # Keep first + last N
        paths_to_keep = [paths[0]] + paths[-(self.image_context_length) :]

        # Remove others and update size tracking
        for path in paths:
            if path not in paths_to_keep:
                image_data = self._image_cache[path]
                self._cache_size_mb -= len(image_data) / (1024 * 1024)
                del self._image_cache[path]

        logger.debug(f"Pruned images from cache, new cache size: ({self._cache_size_mb:.2f}MB)")
