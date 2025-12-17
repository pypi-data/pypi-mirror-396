from __future__ import annotations

from typing import Any, Dict

from ...client import ORPCClient


class MasonLabRoutes:
    def __init__(self, client: ORPCClient) -> None:
        self._client = client

    def get(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "masonlab", "get"], data)

    def save(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "masonlab", "save"], data)
