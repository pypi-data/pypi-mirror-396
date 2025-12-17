from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

import requests


class RigbySDKError(Exception):
    """Raised when the Rigby API returns an error or unexpected payload."""


class ORPCClient:
    """Minimal ORPC-compatible client over HTTP."""

    def __init__(
        self,
        token: str,
        base_url: str = "https://api.rigby.host",
        timeout: int | float = 30,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def _build_url(self, path: Iterable[str]) -> str:
        return f"{self.base_url}/{'/'.join(path)}"

    def call(
        self,
        path: Iterable[str],
        data: Optional[Dict[str, Any]] = None,
        method: str = "POST",
    ) -> Any:
        url = self._build_url(path)
        payload: Dict[str, Any] = {} if data is None else {"json": data}

        response = self.session.request(
            method,
            url,
            json=payload,
            timeout=self.timeout,
        )

        if not response.ok:
            raise RigbySDKError(
                f"Rigby API error {response.status_code}: {response.text}"
            )

        # Try to decode JSON and unwrap ORPC envelope (`{"json": ...}`).
        try:
            parsed = response.json()
        except ValueError:
            return response.text

        if isinstance(parsed, dict) and "json" in parsed:
            return parsed.get("json")
        return parsed
