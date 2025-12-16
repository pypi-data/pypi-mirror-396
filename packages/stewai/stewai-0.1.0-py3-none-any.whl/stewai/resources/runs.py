from __future__ import annotations

from typing import Any, Dict, Optional
import time

import httpx

from ..errors import ApiError, AuthenticationError, RateLimitError


class RunsResource:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def create(self, recipe_id: str, inputs: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        return self._json(self._client.post("runs/", json={"recipe_id": recipe_id, "inputs": inputs or {}}))

    def get(self, run_id: str) -> Dict[str, Any]:
        return self._json(self._client.get(f"runs/{run_id}/"))

    def steps(self, run_id: str) -> Dict[str, Any]:
        return self._json(self._client.get(f"runs/{run_id}/steps/"))

    def wait(self, run_id: str, *, timeout: float = 300.0, poll_interval: float = 1.0) -> Dict[str, Any]:
        deadline = time.time() + timeout
        while True:
            run = self.get(run_id)
            status = run.get("status")
            if status in {"done", "failed", "abandoned"}:
                return run
            if time.time() > deadline:
                raise ApiError(status_code=408, body=run, message="Timed out waiting for run")
            time.sleep(poll_interval)

    def _json(self, res: httpx.Response) -> Dict[str, Any]:
        if res.status_code in (401, 403):
            raise AuthenticationError(status_code=res.status_code, body=_safe_json(res), message="Unauthorized")
        if res.status_code == 429:
            err = RateLimitError(status_code=429, body=_safe_json(res), message="Rate limited")
            err.retry_after = res.headers.get("Retry-After")
            raise err
        if res.status_code < 200 or res.status_code >= 300:
            raise ApiError(status_code=res.status_code, body=_safe_json(res))
        data = _safe_json(res)
        return data if isinstance(data, dict) else {"data": data}


def _safe_json(res: httpx.Response) -> Any:
    try:
        return res.json()
    except Exception:
        return res.text
