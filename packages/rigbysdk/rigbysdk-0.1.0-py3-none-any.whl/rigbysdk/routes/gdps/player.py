from __future__ import annotations

from typing import Any, Dict

from ...client import ORPCClient


class PlayerSongsRoutes:
    def __init__(self, client: ORPCClient) -> None:
        self._client = client

    def list(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "player", "songs", "list"], data)

    def create(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "player", "songs", "create"], data)

    def createFromNewgrounds(self, data: Dict[str, Any]) -> Any:
        return self._client.call(
            ["rpc", "gdps", "player", "songs", "createFromNewgrounds"], data
        )

    def createFromUrl(self, data: Dict[str, Any]) -> Any:
        return self._client.call(
            ["rpc", "gdps", "player", "songs", "createFromUrl"], data
        )


class PlayerRoutes:
    def __init__(self, client: ORPCClient) -> None:
        self._client = client
        self.songs = PlayerSongsRoutes(client)

    def login(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "player", "login"], data)

    def profile(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "player", "profile"], data)
