from collections import Counter
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .base import NightEvent
    from .player import Player
    from .server import Server


class IVote:
    def __init__(self):
        self._vote_info = {}

    def get_vote_info(self):
        return self._vote_info.copy()

    def vote(self, author: "Player", target: Any):
        self._vote_info[author] = target

    def get_players_participating_in_voting(self):
        return []

    def is_all_players_voted(self):
        return len(self._vote_info) >= len(self.get_players_participating_in_voting())

    def get_result_voting(self):
        counter = Counter(self._vote_info.values())
        max_quantity_voted = max(counter.values())

        target_list = []

        for target, quantity in counter.items():
            if quantity == max_quantity_voted:
                target_list.append(target)

        return target_list

    def clear_cache_voting(self):
        self._vote_info.clear()


class IActionable:
    def __init__(self, server: "Server"):
        self.server = server

        self.is_night_activity = True

    async def try_new_night_event(self, player: "Player") -> Optional["NightEvent"]:
        if not self.is_night_activity:
            return

        event = await self.new_night_event(player)
        self.server.night_events.append(event)

        return event

    async def new_night_event(self, player: Optional["Player"] = None) -> "NightEvent":
        pass

    def is_valid(self, player: "Player") -> bool:
        return True

    async def perform_action(self, player: Optional["Player"] = None):
        pass
