from __future__ import annotations

from typing import Any, Dict

from ..client import ORPCClient


class UserRoutes:
    def __init__(self, client: ORPCClient) -> None:
        self._client = client

    def me(self) -> Any:
        return self._client.call(["rpc", "user", "me"])

    def updateProfile(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "user", "updateProfile"], data)

    def listSessions(self) -> Any:
        return self._client.call(["rpc", "user", "listSessions"])

    def revokeSession(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "user", "revokeSession"], data)

    def revokeAllSessions(self) -> Any:
        return self._client.call(["rpc", "user", "revokeAllSessions"])

    def deleteAccount(self) -> Any:
        # Matches TS SDK: confirmation string is set internally.
        return self._client.call(
            ["rpc", "user", "deleteAccount"],
            {"confirmation": "delete"},
        )
