from __future__ import annotations

from typing import Any, Dict

from ...client import ORPCClient


class QuestsRoutes:
    def __init__(self, client: ORPCClient) -> None:
        self._client = client

    def list(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "quests", "list"], data)

    def create(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "quests", "create"], data)

    def remove(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "quests", "remove"], data)
