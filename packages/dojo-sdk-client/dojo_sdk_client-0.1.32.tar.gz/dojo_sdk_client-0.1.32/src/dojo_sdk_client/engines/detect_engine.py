import os
from typing import Optional

from dojo_sdk_core.settings import settings

from .dojo_engine import DojoEngine
from .engine import Engine


def select_engine(api_key: Optional[str] = None) -> Engine:
    if api_key is None:
        api_key = os.getenv("DOJO_API_KEY")

    if settings.engine == "browserbase":
        from .browserbase_engine import BrowserBaseEngine

        return BrowserBaseEngine(
            api_key=os.getenv("BROWSERBASE_API_KEY"),
            project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
            dojo_api_key=api_key,
        )
    else:
        return DojoEngine(api_key=api_key)
