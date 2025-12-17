from __future__ import annotations

import os
from importlib.metadata import PackageNotFoundError, version

import httpx

from .resources.runs import RunsResource

DEFAULT_BASE_URL = "https://api.stewai.com/v1"
ENV_API_KEY = "STEWAI_API_KEY"


def _package_version() -> str:
    try:
        return version("stewai")
    except PackageNotFoundError:  # pragma: no cover
        return "0.0.0"


class Client:
    """StewAI API client."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        resolved_key = api_key or os.environ.get(ENV_API_KEY)
        if not resolved_key:
            raise ValueError(
                f"API key required: pass api_key= or set {ENV_API_KEY} environment variable"
            )

        base_url = base_url.rstrip("/") + "/"
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            transport=transport,
            headers={
                "Authorization": f"Bearer {resolved_key}",
                "User-Agent": f"stewai-python/{_package_version()}",
            },
        )
        self.runs = RunsResource(self._client)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


Stew = Client
