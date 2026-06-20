from random import choice
from typing import TYPE_CHECKING, Optional

from .base import NightEvent, PlayerGroup
from .enums import ActionNightEnum, TeamEnum
from .interfaces import IActionable

if TYPE_CHECKING:
    from .player import Player
    from .server import Server
    from .roles import GodFather


class Team(PlayerGroup):
    def __init__(self, title: TeamEnum):
        super().__init__()

        self.title = title

    def __repr__(self):
        return self.title


class OtherTeam(Team):
    def __init__(self):
        super().__init__(TeamEnum.OTHER)


class ActiveTeam(Team, IActionable):
    def __init__(self, title: TeamEnum, server: "Server"):
        Team.__init__(self, title=title)
        IActionable.__init__(self, server)


class MafiaTeam(ActiveTeam):
    def __init__(self, server: "Server", **kwargs):
        super().__init__(title=TeamEnum.MAFIA, server=server, **kwargs)

        self.godfather: Optional["GodFather"] = None

    def get_players_can_kill(self):
        players = self.get_players_participating_in_voting()
        if self.godfather:
            players.remove(self.godfather.id)

        return players

    async def new_night_event(self, target: Optional["Player"] = None) -> "NightEvent":
        mafia_players = self.get_players_can_kill()

        if len(mafia_players) > 0:
            author = choice(mafia_players)
        elif self.godfather:
            author = self.godfather
        else:
            raise AttributeError('Не кому убивать')

        return NightEvent(ActionNightEnum.KILL, author, target)
