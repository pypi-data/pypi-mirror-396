from __future__ import annotations

import random
import time
from typing import Any, Dict, Mapping, Optional

import httpx

from ..errors import (
    ApiError,
    AuthenticationError,
    RateLimitError,
    RunBlockedError,
    RunCancelledError,
    RunFailedError,
    StewAITimeoutError,
)

TERMINAL_SUCCESS = {"done"}
TERMINAL_ERROR = {"failed", "cancelled", "blocked"}
TERMINAL_STATES = TERMINAL_SUCCESS | TERMINAL_ERROR


class RunsResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def create(
        self,
        recipe_id: str,
        inputs: Optional[Mapping[str, str]] = None,
        *,
        wait: bool = True,
        timeout: float = 300.0,
        poll_interval: float = 0.5,
        max_poll_interval: float = 5.0,
    ) -> Dict[str, Any]:
        run = self._json(
            self._client.post(
                "runs/", json={"recipe_id": recipe_id, "inputs": dict(inputs or {})}
            )
        )
        if not wait:
            return run
        return self.wait(
            run_id=str(run.get("id", "")),
            timeout=timeout,
            poll_interval=poll_interval,
            max_poll_interval=max_poll_interval,
        )

    def get(self, run_id: str) -> Dict[str, Any]:
        return self._json(self._client.get(f"runs/{run_id}/"))

    def steps(self, run_id: str) -> Dict[str, Any]:
        return self._json(self._client.get(f"runs/{run_id}/steps/"))

    def wait(
        self,
        run_id: str,
        *,
        timeout: float = 300.0,
        poll_interval: float = 0.5,
        max_poll_interval: float = 5.0,
    ) -> Dict[str, Any]:
        deadline = time.time() + timeout
        current_interval = max(0.0, poll_interval)
        max_interval = max(0.0, max_poll_interval)
        last_status = "unknown"

        while True:
            # Check deadline at the start of each iteration to catch rate-limit spin
            if time.time() >= deadline:
                raise StewAITimeoutError(
                    run_id=run_id, timeout=timeout, last_status=last_status
                )

            try:
                run = self.get(run_id)
            except RateLimitError as e:
                retry_after = _parse_retry_after_seconds(e.retry_after)
                if retry_after is None:
                    raise
                sleep_time = _cap_to_deadline(retry_after, deadline)
                if sleep_time > 0:
                    self._sleep(sleep_time)
                # Loop will check deadline at next iteration
                continue

            status = str(run.get("status", "unknown"))
            last_status = status

            if status in TERMINAL_STATES:
                return self._handle_terminal(run, status)

            sleep_time = self._next_interval(current_interval, max_interval)
            sleep_time = _cap_to_deadline(sleep_time, deadline)
            if sleep_time <= 0:
                continue
            self._sleep(sleep_time)

            if current_interval == 0:
                continue
            current_interval = min(current_interval * 1.5, max_interval)

    def _sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def _handle_terminal(self, run: Dict[str, Any], status: str) -> Dict[str, Any]:
        if status in TERMINAL_SUCCESS:
            return run

        run_id = str(run.get("id", "unknown"))
        if status == "failed":
            raise RunFailedError(run_id=run_id, run=run)
        if status == "cancelled":
            raise RunCancelledError(run_id=run_id, run=run)
        if status == "blocked":
            raise RunBlockedError(run_id=run_id, run=run)
        raise RunFailedError(run_id=run_id, run=run)

    def _next_interval(self, current: float, maximum: float) -> float:
        if current <= 0:
            return 0.0
        if maximum <= 0:
            maximum = current

        jitter = current * 0.2 * (2.0 * random.random() - 1.0)
        return min(max(0.0, current + jitter), maximum)

    def _json(self, res: httpx.Response) -> Dict[str, Any]:
        if res.status_code in (401, 403):
            raise AuthenticationError(
                status_code=res.status_code,
                body=_safe_json(res),
                message="Unauthorized",
            )
        if res.status_code == 429:
            err = RateLimitError(
                status_code=429, body=_safe_json(res), message="Rate limited"
            )
            err.retry_after = res.headers.get("Retry-After")
            raise err
        if res.status_code < 200 or res.status_code >= 300:
            raise ApiError(status_code=res.status_code, body=_safe_json(res))

        data = _safe_json(res)
        return data if isinstance(data, dict) else {"data": data}


def _cap_to_deadline(seconds: float, deadline: float) -> float:
    remaining = deadline - time.time()
    if remaining <= 0:
        return 0.0
    return min(seconds, remaining)


def _parse_retry_after_seconds(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    try:
        val = float(value)
    except Exception:
        return None
    if val <= 0:
        return None
    return val


def _safe_json(res: httpx.Response) -> Any:
    try:
        return res.json()
    except Exception:
        return res.text
