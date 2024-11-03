from random import choice
from typing import TYPE_CHECKING

from .active_player import ActivePlayer, ActiveTeamPlayer
from .base import PlayerGroup, NightEvent
from .enums import TeamEnum, ServerState
from .settings import Settings
from .singal import ServerSignals
from .teams import Team, MafiaTeam

if TYPE_CHECKING:
    from .player import PrePlayer


class Server(PlayerGroup):
    def __init__(self):
        super().__init__()

        self.signals = ServerSignals()
        self.settings = Settings(self)

        self.days = 0
        self.state = ServerState.NIGHT

        self.civilian_team = Team(TeamEnum.CIVILIAN)
        self.active_teams = {
            TeamEnum.MAFIA: MafiaTeam(self)
        }

        self.night_events = []

    async def _change_state(self, value):
        self.state = value
        await self.signals.on_change_server_state.emit(value)

    async def day(self):
        self.days += 1
        self.night_events.clear()
        await self._change_state(ServerState.DAY)

    async def night(self):
        self.clear_cache_voting()
        await self._change_state(ServerState.NIGHT)

    def get_active_night_players(self, priority: int = 1):
        players = self.get_players_alive()
        return players.filter(
            lambda player:
            isinstance(player, ActivePlayer) and player.priority == priority and
            (not isinstance(player, ActiveTeamPlayer) or player.is_wakes_up_separately)
            and player.is_night_activity
        )

    def check_win(self) -> Team | None:
        players = self.get_players_alive()

        other_players = players.filter(lambda player: player.team.title == TeamEnum.OTHER)
        if len(other_players) == 1 and len(players) <= 2:
            return other_players.to_list()[0].team

        if self.civilian_team.get_players_alive() == players:
            return self.civilian_team

        teams = {title: len(team.get_players_alive()) for title, team in self.active_teams.items()}

        for team, quantity_players in teams.items():
            if quantity_players >= len(players) - quantity_players:
                return self.active_teams[team]

    def get_night_events(self) -> list[NightEvent]:
        self.night_events.sort()
        return self.night_events.copy()

    async def process_night_events(self):
        events = self.get_night_events()
        for event in events:
            await event.author.perform_action(event.target)

    def distribute_roles(self, pre_players: list["PrePlayer"], role_counts: dict[type, int]):
        for role, count in role_counts.items():
            for _ in range(count):
                player = choice(pre_players)
                player_role = role(player.id, player.username, self)
                self.add_player(player.id, player_role)
                pre_players.remove(player)

        return self.players
