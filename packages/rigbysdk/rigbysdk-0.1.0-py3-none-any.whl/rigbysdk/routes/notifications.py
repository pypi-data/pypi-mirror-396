from __future__ import annotations

from typing import Any, Dict, Optional

from ..client import ORPCClient


class NotificationRoutes:
    def __init__(self, client: ORPCClient) -> None:
        self._client = client

    def list(self) -> Any:
        return self._client.call(["rpc", "notifications", "list"])

    def markAsRead(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "notifications", "markAsRead"], data)

    def markAllAsRead(self) -> Any:
        return self._client.call(["rpc", "notifications", "markAllAsRead"])

    def delete(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "notifications", "delete"], data)
