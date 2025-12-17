from __future__ import annotations

from typing import Any, Dict

from ...client import ORPCClient


class LevelsRoutes:
    def __init__(self, client: ORPCClient) -> None:
        self._client = client

    def search(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "levels", "search"], data)

    def get(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "levels", "details"], data)

    def updateMetadata(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "levels", "updateMetadata"], data)

    def updateMusic(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "levels", "updateMusic"], data)

    def updateRating(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "levels", "updateRating"], data)
