from __future__ import annotations

from typing import Any, Dict

from ...client import ORPCClient


class RolesRoutes:
    def __init__(self, client: ORPCClient) -> None:
        self._client = client

    def list(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "roles", "list"], data)

    def create(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "roles", "create"], data)

    def update(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "roles", "update"], data)

    def remove(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "roles", "delete"], data)
