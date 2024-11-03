from dataclasses import field, dataclass

from src.store.repository import Repository
from .active_player import ActivePlayer
from .enums import ActionNightEnum
from .interfaces import IVote
from .player import Player


class PlayerGroup(IVote):
    def __init__(self):
        super().__init__()

        self.players = Repository[Player]()

    def add_player(self, id: int, player: Player):
        self.players.add(id, player)

    def get_players_alive(self) -> Repository[Player]:
        return self.players.filter(lambda player: player.is_alive)

    def get_players_participating_in_voting(self) -> Repository[Player]:
        players_alive = self.get_players_alive()
        return players_alive.filter(lambda player: player.is_can_vote)


@dataclass
class NightEvent:
    action: ActionNightEnum
    author: ActivePlayer
    target: Player | str | None
    data: object = field(default=None)

    def __lt__(self, other):
        return self.action < other.action
