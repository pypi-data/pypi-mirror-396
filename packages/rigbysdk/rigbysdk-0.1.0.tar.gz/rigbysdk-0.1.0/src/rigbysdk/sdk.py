from __future__ import annotations

from .client import ORPCClient
from .routes.notifications import NotificationRoutes
from .routes.user import UserRoutes
from .routes.gdps.analytics import AnalyticsRoutes
from .routes.gdps.config import ConfigRoutes
from .routes.gdps.gauntlets import GauntletsRoutes
from .routes.gdps.levels import LevelsRoutes
from .routes.gdps.mappacks import MapPacksRoutes
from .routes.gdps.masonlab import MasonLabRoutes
from .routes.gdps.music import MusicRoutes
from .routes.gdps.player import PlayerRoutes
from .routes.gdps.players import PlayersRoutes
from .routes.gdps.public import PublicRoutes
from .routes.gdps.quests import QuestsRoutes
from .routes.gdps.roles import RolesRoutes
from .routes.gdps.server import ServerRoutes


class GDPSRoutes:
    def __init__(self, client: ORPCClient) -> None:
        self.config = ConfigRoutes(client)
        self.analytics = AnalyticsRoutes(client)
        self.gauntlets = GauntletsRoutes(client)
        self.levels = LevelsRoutes(client)
        self.mappacks = MapPacksRoutes(client)
        self.masonlab = MasonLabRoutes(client)
        self.music = MusicRoutes(client)
        self.player = PlayerRoutes(client)
        self.players = PlayersRoutes(client)
        self.public = PublicRoutes(client)
        self.quests = QuestsRoutes(client)
        self.roles = RolesRoutes(client)
        self.server = ServerRoutes(client)


class RigbySDK:
    """Python SDK mirroring the TypeScript interface."""

    def __init__(self, token: str, base_url: str = "https://api.rigby.host") -> None:
        client = ORPCClient(token, base_url=base_url)
        self.client = client
        self.gdps = GDPSRoutes(client)
        self.notifications = NotificationRoutes(client)
        self.user = UserRoutes(client)
