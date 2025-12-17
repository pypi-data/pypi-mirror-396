from __future__ import annotations

from typing import Any, Dict

from ...client import ORPCClient


class PublicRoutes:
    def __init__(self, client: ORPCClient) -> None:
        self._client = client

    def page(self, data: Dict[str, Any]) -> Any:
        return self._client.call(["rpc", "gdps", "public", "page"], data)
