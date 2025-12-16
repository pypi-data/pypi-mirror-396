from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


class StewError(Exception):
    pass


@dataclass
class ApiError(StewError):
    status_code: int
    body: Any = None
    message: str = "API request failed"


class AuthenticationError(ApiError):
    pass


class RateLimitError(ApiError):
    retry_after: Optional[str] = None
