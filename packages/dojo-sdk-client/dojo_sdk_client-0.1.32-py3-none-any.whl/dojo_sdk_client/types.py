import enum
from dataclasses import dataclass
from typing import Any, Optional

from dojo_sdk_core.ws_types import HistoryStep


class TaskStatus(str, enum.Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    TIMEOUT = "TIMEOUT"


class NoRunnersAvailableError(Exception):
    """Error when no runners are available"""

    pass


@dataclass
class TaskResponse:
    """Response from task status endpoint"""

    status: TaskStatus
    screenshot: Optional[str]
    history: Optional[list[HistoryStep]]
    step: Optional[int]
    state: Optional[dict[str, Any]] = None
    failure_reason: Optional[str] = None
