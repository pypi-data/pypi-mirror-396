from importlib.metadata import PackageNotFoundError, version

from .client import Client, Stew
from .errors import (
    ApiError,
    AuthenticationError,
    RateLimitError,
    RunBlockedError,
    RunCancelledError,
    RunError,
    RunFailedError,
    StewAIError,
    StewAITimeoutError,
    StewError,
)

try:
    __version__ = version("stewai")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = [
    "Client",
    "Stew",
    "__version__",
    "StewAIError",
    "StewError",
    "ApiError",
    "AuthenticationError",
    "RateLimitError",
    "RunError",
    "RunFailedError",
    "RunCancelledError",
    "RunBlockedError",
    "StewAITimeoutError",
]
