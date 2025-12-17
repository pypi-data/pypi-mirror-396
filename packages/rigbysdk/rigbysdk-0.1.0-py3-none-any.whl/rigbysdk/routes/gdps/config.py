from __future__ import annotations

from typing import Any, Dict

from ...client import ORPCClient


class ConfigRoutes:
    def __init__(self, client: ORPCClient) -> None:
        self._client = client

    def get(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "config", "get"], data)

    def updateChests(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "config", "updateChest"], data)

    def updateSecurity(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "config", "updateSecurity"], data)

    def updateServer(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "config", "updateServer"], data)
