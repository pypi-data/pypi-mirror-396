from __future__ import annotations

from typing import Any, Dict

from ...client import ORPCClient


class ServerRoutes:
    def __init__(self, client: ORPCClient) -> None:
        self._client = client

    def listMembers(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "listMembers"], data)

    def listInvites(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "listInvites"], data)

    def createInvite(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "createInvite"], data)

    def revokeInvite(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "revokeInvite"], data)

    def join(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "join"], data)

    def updateMember(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "updateMember"], data)

    def removeMember(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "removeMember"], data)

    def leave(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "leave"], data)

    def list(self) -> Any:
        return self._client.call(["rpc", "gdps", "list"])

    def mysrvs(self) -> Any:
        return self._client.call(["rpc", "gdps", "mysrvs"])

    def createsrv(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "createsrv"], data)

    def deletesrv(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "deletesrv"], data)

    def getinfo(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "getinfo"], data)

    def togglePublic(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "togglePublic"], data)

    def submitExternal(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "submitExternal"], data)
