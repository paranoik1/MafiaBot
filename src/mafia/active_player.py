from typing import TYPE_CHECKING

from src.mafia.interfaces import IActionable
from src.mafia.player import Player

if TYPE_CHECKING:
    from src.mafia.server import Server
    from src.mafia.teams import Team


class ActivePlayer(Player, IActionable):
    def __init__(self, id: int, username: str, server: "Server", team: "Team", priority: int = 1):
        Player.__init__(self, id, username, server, team)
        IActionable.__init__(self, server)

        self.priority = priority

    def get_target_list(self):
        return self.server.get_players_alive()


class ActiveTeamPlayer(ActivePlayer):
    def __init__(self, *args, is_wakes_up_separately: bool = False, **kwargs):
        super().__init__(*args, **kwargs)

        # Просыпается ли отдельно
        self.is_wakes_up_separately = is_wakes_up_separately

    def vote(self, target: Player):
        if not self.is_night_activity:
            return

        self.team.vote(self, target)
