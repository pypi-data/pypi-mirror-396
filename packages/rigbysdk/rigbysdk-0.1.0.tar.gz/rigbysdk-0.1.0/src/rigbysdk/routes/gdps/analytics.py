from __future__ import annotations

from typing import Any, Dict

from ...client import ORPCClient


class AnalyticsRoutes:
    def __init__(self, client: ORPCClient) -> None:
        self._client = client

    def overview(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "analytics", "overview"], data)
