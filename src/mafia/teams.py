from random import choice
from typing import TYPE_CHECKING

from .base import PlayerGroup, NightEvent
from .enums import TeamEnum, ActionNightEnum
from .interfaces import IActionable

if TYPE_CHECKING:
    from .server import Server
    from .player import Player


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
    def __init__(self, server: "Server", *args, **kwargs):
        super().__init__(title=TeamEnum.MAFIA, server=server, *args, **kwargs)

        self.godfather = None

    def get_players_can_kill(self):
        players = self.get_players_participating_in_voting()
        if self.godfather:
            players.remove(self.godfather.id)

        return players

    async def new_night_event(self, target: "Player" = None):
        mafia_players = self.get_players_can_kill()

        if len(mafia_players) > 0:
            author = choice(mafia_players)
        else:
            author = self.godfather

        return NightEvent(ActionNightEnum.KILL, author, target)
