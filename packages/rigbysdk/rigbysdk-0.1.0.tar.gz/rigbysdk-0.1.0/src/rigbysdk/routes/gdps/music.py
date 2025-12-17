from __future__ import annotations

from typing import Any, Dict

from ...client import ORPCClient


class MusicRoutes:
    def __init__(self, client: ORPCClient) -> None:
        self._client = client

    def list(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "music", "list"], data)

    def createFromNewgrounds(self, data: Dict[str, Any]) -> Any:
        return self._client.call(
            ["rpc", "gdps", "music", "createFromNewgrounds"], data
        )

    def createFromUrl(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "music", "createFromUrl"], data)

    def updateMetadata(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "music", "updateMetadata"], data)

    def deleteAll(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "music", "deleteAll"], data)

    def toggleBan(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "music", "toggleBan"], data)
