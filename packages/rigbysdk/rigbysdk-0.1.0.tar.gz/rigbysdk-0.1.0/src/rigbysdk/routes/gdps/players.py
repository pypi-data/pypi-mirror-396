from __future__ import annotations

from typing import Any, Dict

from ...client import ORPCClient


class PlayersRoutes:
    def __init__(self, client: ORPCClient) -> None:
        self._client = client

    def list(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "players", "list"], data)

    def assign(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "players", "assign"], data)
