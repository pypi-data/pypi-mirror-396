from __future__ import annotations

import httpx

from .resources.runs import RunsResource

DEFAULT_BASE_URL = "https://api.stewai.com/v1"


class Stew:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        base_url = base_url.rstrip("/") + "/"
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            transport=transport,
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "stewai-python/0.1.0",
            },
        )
        self.runs = RunsResource(self._client)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "Stew":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
