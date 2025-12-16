from enum import Enum


class TelemetryEvent(str, Enum):
    """Predefined telemetry events for operational monitoring."""

    # Errors
    API_ERROR = "api_error"
    TASK_ERROR = "task_error"
    RUNTIME_ERROR = "runtime_error"
    VALIDATION_ERROR = "validation_error"

    # Network issues
    CONNECTION_ERROR = "connection_error"
    TIMEOUT_ERROR = "timeout_error"
    UNREACHABLE_ENDPOINT = "unreachable_endpoint"

    # Blocking/restrictions
    GEO_BLOCK = "geo_block"
    RATE_LIMIT = "rate_limit"
    AUTH_ERROR = "auth_error"

    # Runtime crashes
    UNHANDLED_EXCEPTION = "unhandled_exception"
    CRASH = "crash"
