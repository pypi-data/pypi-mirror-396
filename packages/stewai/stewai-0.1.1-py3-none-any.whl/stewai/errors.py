from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


class StewAIError(Exception):
    """Base exception for all StewAI SDK errors."""


StewError = StewAIError


@dataclass
class ApiError(StewAIError):
    """HTTP-level API error."""

    status_code: int
    body: Any = None
    message: str = "API request failed"


class AuthenticationError(ApiError):
    """401/403 authentication failure."""


class RateLimitError(ApiError):
    """429 rate limit exceeded."""

    retry_after: Optional[str] = None


@dataclass
class RunError(StewAIError):
    """Base class for run-level errors."""

    run_id: str
    run: dict


class RunFailedError(RunError):
    """Run completed with status='failed'."""


class RunCancelledError(RunError):
    """Run was cancelled (status='cancelled')."""


class RunBlockedError(RunError):
    """Run blocked due to insufficient credits (status='blocked')."""


@dataclass
class StewAITimeoutError(StewAIError):
    """SDK-level timeout waiting for run completion."""

    run_id: str
    timeout: float
    last_status: str
    message: str = "Timed out waiting for run"
