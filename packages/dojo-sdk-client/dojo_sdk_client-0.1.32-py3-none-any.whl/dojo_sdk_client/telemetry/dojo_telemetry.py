import asyncio
import logging
import os
import sys
import traceback
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from functools import wraps
from time import time
from typing import Any, Callable, Dict, Optional

import aiohttp
import requests
from dojo_sdk_core.settings import settings

from .types import TelemetryEvent

logger = logging.getLogger(__name__)


class DojoTelemetry:
    """PostHog telemetry client for operational monitoring."""

    def __init__(
        self,
        base_url: str = "https://us.i.posthog.com",
        timeout: int = 5,
        enabled: bool = True,
        silent: bool = True,
    ):
        self.api_key = settings.posthog_api_key
        self.base_url = base_url.rstrip("/")
        self.distinct_id = f"dojo_client_{uuid.uuid4()}"
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.enabled = enabled
        self.silent = silent

        if not settings.posthog_api_key or settings.posthog_api_key == "":
            if not silent:
                logger.warning("PostHog API key not found in settings, telemetry disabled")
            self.enabled = False
            return

        self._session: Optional[aiohttp.ClientSession] = None

        if not silent:
            logger.info(f"Telemetry enabled: {self.enabled}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Lazy initialize the aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    def _prepare_payload(self, event: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "api_key": self.api_key,
            "event": event,
            "distinct_id": self.distinct_id,
            "properties": properties or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def send_event_async(
        self,
        event: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send an event to PostHog (internal async implementation)."""
        if not self.enabled:
            return False

        try:
            if not self.silent:
                logger.info(f"Sending telemetry event: {event} with properties: {properties}")
            session = await self._get_session()

            payload = self._prepare_payload(event, properties)

            async with session.post(f"{self.base_url}/capture/", json=payload) as response:
                if response.status == 200:
                    if not self.silent:
                        logger.debug(f"Telemetry event sent: {event}")
                    return True
                else:
                    if not self.silent:
                        logger.warning(f"Telemetry failed: {response.status}")
                    return False

        except Exception as e:
            if not self.silent:
                logger.error(f"Telemetry error: {e}")
            return False

    def send_event_sync(
        self,
        event: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send an event to PostHog synchronously using requests."""
        if not self.enabled:
            return False

        try:
            payload = self._prepare_payload(event, properties)
            response = requests.post(f"{self.base_url}/capture/", json=payload, timeout=self.timeout.total)

            if response.status_code == 200:
                if not self.silent:
                    logger.debug(f"Telemetry event sent: {event}")
                return True
            else:
                if not self.silent:
                    logger.warning(f"Telemetry failed: {response.status_code}")
                return False

        except Exception as e:
            if not self.silent:
                logger.error(f"Telemetry error: {e}")
            return False

    @asynccontextmanager
    async def _track_context(self, op_name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager to track operation latency.

        Usage:
            async with telemetry._track_context("api_call", {"endpoint": "/tasks"}):
                await some_operation()
        """
        if not self.enabled:
            logger.info(f"Telemetry not enabled, skipping {op_name}")
            yield
            return

        start = time()
        error = None

        try:
            if not self.silent:
                logger.info(f"Tracking latency for {op_name}")
            yield
        except Exception as e:
            error = e
            if isinstance(e, (aiohttp.ClientError, asyncio.TimeoutError)):
                await self.report_network_error(
                    error=e,
                    endpoint=metadata.get("endpoint", "unknown") if metadata else "unknown",
                    method=metadata.get("method", "GET") if metadata else "GET",
                    metadata={"operation": op_name},
                )
            else:
                await self.report_error(error=e, context={"operation": op_name, **(metadata or {})})
            raise
        finally:
            properties = {
                "latency_ms": (time() - start) * 1000,
                "success": error is None,
                **(metadata or {}),
            }

            if error:
                properties["error_type"] = type(error).__name__
                properties["error_message"] = str(error)

            await self.send_event_async(op_name, properties)

    def track(self, operation: Optional[str] = None, engine: Optional[str] = None):
        """
        Decorator to track function latency.

        Usage:
            @telemetry.track("create_task", engine="browserbase")
            async def create_task():
                ...
        """

        def decorator(func: Callable):
            op_name = operation or func.__name__

            @wraps(func)
            async def wrapper(*args, **kwargs):
                if not self.enabled:
                    return await func(*args, **kwargs)

                dynamic_metadata = self._extract_dynamic_metadata(args, kwargs)

                # Add engine to metadata if provided
                if engine:
                    dynamic_metadata["engine"] = engine

                async with self._track_context(op_name, dynamic_metadata):
                    return await func(*args, **kwargs)

            return wrapper

        return decorator

    def track_sync(self, operation: Optional[str] = None, engine: Optional[str] = None):
        """
        Decorator to track synchronous function latency.

        Usage:
            @telemetry.track_sync("stop_task_sync", engine="browserbase")
            def stop_task_sync():
                ...
        """

        def decorator(func: Callable):
            op_name = operation or func.__name__

            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)

                # Extract dynamic values from function arguments at runtime
                dynamic_metadata = self._extract_dynamic_metadata(args, kwargs)

                # Add engine to metadata if provided
                if engine:
                    dynamic_metadata["engine"] = engine

                start = time()
                error = None

                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error = e
                    raise
                finally:
                    properties = {
                        "latency_ms": (time() - start) * 1000,
                        "success": error is None,
                        **dynamic_metadata,  # Add the extracted metadata here
                    }

                    if error:
                        properties["error_type"] = type(error).__name__
                        properties["error_message"] = str(error)

                    try:
                        self.send_event_sync(op_name, properties)
                    except Exception as telemetry_error:
                        # Never let telemetry errors affect the main function
                        if not self.silent:
                            logger.debug(f"Telemetry send failed: {telemetry_error}")

            return wrapper

        return decorator

    def _extract_dynamic_metadata(self, args: tuple, kwargs: dict) -> Dict[str, Any]:
        """Extract dynamic values from function arguments at runtime"""
        dynamic_metadata = {}
        if "exec_id" in kwargs:
            dynamic_metadata["exec_id"] = kwargs["exec_id"]
        elif len(args) > 1:
            dynamic_metadata["exec_id"] = args[1]

        if "status" in kwargs:
            status = kwargs["status"]
            # Handle both enum and dict/string cases
            if hasattr(status, "value"):
                dynamic_metadata["task_status"] = status.value
            else:
                dynamic_metadata["task_status"] = status
        return dynamic_metadata

    async def report_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: str = "error",
    ):
        """
        Report an error with full context.

        Args:
            error: The exception object
            context: Additional context (e.g., function name, parameters)
            severity: error, warning, critical
        """
        properties = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "severity": severity,
            "traceback": "".join(traceback.format_exception(type(error), error, error.__traceback__)),
            **(context or {}),
        }

        await self.send_event_async(TelemetryEvent.RUNTIME_ERROR, properties)

    async def report_network_error(
        self,
        error: Exception,
        endpoint: str,
        method: str = "GET",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Report network-related errors with automatic classification.
        Detects: timeouts, connection errors, geo-blocking, etc.
        """
        error_type = type(error).__name__
        properties = {
            "endpoint": endpoint,
            "method": method,
            "error_type": error_type,
            "error_message": str(error),
            **(metadata or {}),
        }

        # Classify the error
        if isinstance(error, asyncio.TimeoutError) or "timeout" in str(error).lower():
            event = TelemetryEvent.TIMEOUT_ERROR
            properties["classification"] = "timeout"
        elif isinstance(error, aiohttp.ClientConnectionError):
            event = TelemetryEvent.UNREACHABLE_ENDPOINT
            properties["classification"] = "connection_failed"
        elif hasattr(error, "status"):
            properties["status_code"] = error.status

            if error.status == 403:
                event = TelemetryEvent.GEO_BLOCK
                properties["classification"] = "geo_block_or_forbidden"
            elif error.status == 401:
                event = TelemetryEvent.AUTH_ERROR
                properties["classification"] = "unauthorized"
            elif error.status == 429:
                event = TelemetryEvent.RATE_LIMIT
                properties["classification"] = "rate_limited"
            else:
                event = TelemetryEvent.API_ERROR
                properties["classification"] = f"http_{error.status}"
        else:
            event = TelemetryEvent.CONNECTION_ERROR
            properties["classification"] = "unknown_network_error"

        await self.send_event_async(event, properties)

    def setup_crash_handler(self):
        """
        Setup global exception handler to catch unhandled exceptions.
        Call this once during app initialization.
        """
        if not self.enabled:
            return

        def exception_handler(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            properties = {
                "error_type": exc_type.__name__,
                "error_message": str(exc_value),
                "traceback": "".join(traceback.format_exception(exc_type, exc_value, exc_traceback)),
                "severity": "critical",
            }

            # Send telemetry synchronously cause async loop may be already dead
            self.send_event_sync(TelemetryEvent.CRASH, properties)

            # Call the default exception handler
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

        sys.excepthook = exception_handler

    async def close(self):
        """Close the telemetry client."""
        if self._session and not self._session.closed:
            await self._session.close()


enabled = os.getenv("TELEMETRY_ENABLED", "true").lower() == "true"
silent = os.getenv("TELEMETRY_SILENT", "true").lower() == "true"
telemetry = DojoTelemetry(enabled=enabled, silent=silent)
